class FileTransferWithSSH:
    """
    使用 Paramiko 和 SCP 通过 SSH 密钥认证传输文件的工具类。
    """

    def __init__(self, remote_server, username='root', port=22, pkey_path=None):
        """
        初始化 FileTransferWithSSH 类并建立与 B 服务器的 SSH 连接。

        :param remote_server: 远端服务器的 IP 地址 (str)
        :param username: 远端服务器的用户名 (str)，默认为 'root'
        :param port: 远端服务器的 SSH 端口 (int)，默认为 22
        :param pkey_path: 当前服务器上的私钥文件路径 (str)
        """
        self.remote_server = remote_server
        self.username = username
        self.port = port
        self.private_key_path = pkey_path or os.path.join(os.path.expanduser('~'), '.ssh/id_rsa')
        self.private_key_path = os.path.normpath(self.private_key_path)
        self.ssh = None
        self.is_connected = False  # 添加连接状态属性

        # 在初始化时尝试建立连接
        self._connect()

    def load_private_key(self, key_path):
        """自动尝试加载不同类型的私钥"""
        for key_type in [
            paramiko.RSAKey,
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
            paramiko.DSSKey,
        ]:
            try:
                return key_type.from_private_key_file(key_path)
            except (paramiko.SSHException, ValueError, OSError):
                continue
        raise ValueError(f"无法加载私钥 {key_path}，可能格式不支持或文件损坏")

    def _connect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 加载私钥
            private_key = self.load_private_key(self.private_key_path)

            # 连接到 B 服务器
            self.ssh.connect(
                hostname=self.remote_server,
                port=self.port,
                username=self.username,
                pkey=private_key
            )
            self.is_connected = True  # 更新连接状态为成功
            return {'status': 'success', 'message': 'SSH 连接成功'}
        except Exception as e:
            self.is_connected = False  # 更新连接状态为失败
            return {'status': 'failure', 'message': f'SSH 连接失败: {str(e)}'}

    def scp_file(self, a_file_path, b_file_path):
        """ 从 A(当前) 服务器传输到 B(远端) 服务器
        :param a_file_path:
        :param b_file_path:
        :return:
        """
        try:
            if not self.is_connected:  # 检查连接状态
                self._connect()  # 自动重连

            if not self.is_connected:  # 如果重连仍失败，直接返回错误
                return {'status': 'failure', 'message': '无法传输文件，原因：未建立有效的 SSH 连接'}

            # 获取远端文件的父目录路径
            remote_dir = os.path.dirname(b_file_path)
            # 在远端服务器上创建目录（如果不存在）
            stdin, stdout, stderr = self.ssh.exec_command(f"mkdir -p {remote_dir} && chmod 755 {remote_dir}")
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                return {'status': 'failure', 'message': f'创建远端目录失败: {stderr.read().decode()}'}

            with SCPClient(self.ssh.get_transport()) as scp:
                scp.put(a_file_path, b_file_path)

            return {'status': 'success', 'message': '文件传输成功'}
        except Exception as e:
            self.is_connected = False  # 如果传输失败，更新连接状态
            return {'status': 'failure', 'message': f'文件传输失败: {str(e)}'}

    def scp_file_object(self, file_obj, b_file_path):
        """
        将文件对象直接传输到 B(远端) 服务器。

        :param file_obj: 文件对象 (支持 read 方法的对象)
        :param b_file_path: B(远端) 服务器上的目标路径 (str)
        :return: 成功或失败的状态信息 (dict)
        """
        try:
            if not self.is_connected:  # 检查连接状态
                self._connect()  # 自动重连

            if not self.is_connected:  # 如果重连仍失败，直接返回错误
                return {'status': 'failure', 'message': '无法传输文件，原因：未建立有效的 SSH 连接'}

            with SCPClient(self.ssh.get_transport()) as scp:
                # 使用 putfo 方法直接传输文件对象
                scp.putfo(file_obj, b_file_path)

            return {'status': 'success', 'message': '文件对象传输成功'}
        except Exception as e:
            self.is_connected = False  # 如果传输失败，更新连接状态
            return {'status': 'failure', 'message': f'文件对象传输失败: {str(e)}'}

    @staticmethod
    def get_file_object(local_file_path):
        """
        根据本地文件路径返回一个文件对象。

        :param local_file_path: 本地文件路径 (str)
        :return: 文件对象 或 错误信息 (tuple)
        """
        try:
            if not Path(local_file_path).exists():
                return {'status': 'failure', 'message': f'文件不存在: {local_file_path}'}
            return open(local_file_path, 'rb')
        except Exception as e:
            return {'status': 'failure', 'message': f'无法打开文件: {str(e)}'}

    @staticmethod
    def get_file_content(local_file_path):
        """
        根据本地文件路径读取文件内容。

        :param local_file_path: 本地文件路径 (str)
        :return: 文件内容 或 错误信息 (dict)
        """
        try:
            if not Path(local_file_path).exists():
                return {'status': 'failure', 'message': f'文件不存在: {local_file_path}'}
            with open(local_file_path, 'rb') as file_obj:
                content = file_obj.read()
                return {'status': 'success', 'message': '文件内容读取成功', 'content': content}
        except Exception as e:
            return {'status': 'failure', 'message': f'文件内容读取失败: {str(e)}'}

    def read_remote_file_content(self, remote_file_path):
        """
        通过 SSH 读取远程服务器上的文件内容。

        :param remote_file_path: 远程服务器上的文件路径 (str)
        :return: 文件内容 或 错误信息 (dict)
        """
        try:
            if not self.is_connected:  # 检查连接状态
                self._connect()  # 自动重连

            if not self.is_connected:  # 如果重连仍失败，直接返回错误
                return {'status': 'failure', 'message': '无法读取远程文件，原因：未建立有效的 SSH 连接'}

            # 使用 SFTP 读取远程文件内容
            with self.ssh.open_sftp() as sftp:
                with sftp.open(remote_file_path, 'rb') as remote_file:
                    _content = remote_file.read()
            return {
                'status': 'success',
                'message': '远程文件内容读取成功',
                'sftp': sftp,
                'file_obj': remote_file,
                'content': _content,
            }
        except Exception as e:
            return {'status': 'failure', 'message': f'远程文件内容读取失败: {str(e)}'}

    def read_remote_file_bytesio(self, remote_file_path):
        """
        通过 SSH 读取远程服务器上的文件 BytesIO。

        :param remote_file_path: 远程服务器上的文件路径 (str)
        :return: 文件内容 或 错误信息 (dict)
        """
        try:
            if not self.is_connected:  # 检查连接状态
                self._connect()  # 自动重连

            if not self.is_connected:  # 如果重连仍失败，直接返回错误
                return {'status': 'failure', 'message': '无法读取远程文件，原因：未建立有效的 SSH 连接'}

            # 使用 SFTP 读取远程文件内容
            with self.ssh.open_sftp() as sftp:
                with sftp.file(remote_file_path, 'rb') as remote_file:
                    # 将远程文件内容读取到BytesIO对象中
                    _buffer = BytesIO(remote_file.read())
            return {
                'status': 'success',
                'message': '远程文件内容读取成功',
                'sftp': sftp,
                'file_obj': remote_file,
                'buffer': _buffer,
            }
        except Exception as e:
            return {'status': 'failure', 'message': f'远程文件内容读取失败: {str(e)}'}

    def remote_file_exists(self, remote_path):
        """
        判断远端文件是否存在

        :param remote_path: 远端文件路径
        :return: bool
        """
        try:
            with self.ssh.open_sftp() as sftp:
                stats = sftp.stat(remote_path)  # 获取文件状态
                return True, stats
        except IOError:
            return False, str(IOError)
        except Exception as e:
            return False, f"发生错误: {e}"

    def close(self):
        if self.ssh:
            self.ssh.close()
            self.ssh = None
            return {'status': 'success', 'message': '远程连接已关闭'}
        return {'status': 'failure', 'message': '没有需要关闭的连接'}


remote_storage_server = FileTransferWithSSH(remote_server=settings.REMOTE_STORAGE_SERVERIP)
