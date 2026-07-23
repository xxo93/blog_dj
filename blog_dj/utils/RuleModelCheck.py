class ModelValidator:
    """
    通用校验主类：
    1.  直接注册规则类（无需实例化）
    2.  validate仅接收model和data参数
    3.  调用run()方法执行校验并返回字符串结果
    """
    def __init__(self):
        # 注册表：键为model名称，值为对应的 model_en ”规则类（非实例）“、”额外参数字典“
        self.model_rule_map = {}
        # 缓存待校验的参数（model + data）
        self.pending_model = None
        self.pending_data = None

    def register_model_rules(self, model, rule_class, **rule_kwargs):
        """
        直接注册 model_en 规则类（无需实例化，传入类本身即可）
        :param model:  model_en 名称（字符串，如"Traceback"）
        :param rule_class: 对应 model_en 的规则类（如TracebackRules）
        :param rule_kwargs: 该模型校验规则的额外参数（全局/通用参数）
        """
        # 校验传入的是类类型
        if not isinstance(rule_class, type):
            raise TypeError(f"传入的{rule_class.__name__ if hasattr(rule_class, '__name__') else rule_class}"
                            f"必须是一个类（而非实例或其他类型）")
        # 存储规则类 + 额外参数
        self.model_rule_map[model] = (rule_class, rule_kwargs)
        return self  # 支持链式调用

    def validate(self, model, data):
        """
        仅接收model和data两个参数，缓存待校验信息（不立即执行校验）
        :param model: 目标 model_en 名称
        :param data: 待校验数据（任意类型）
        :return: self 支持链式调用（如 validator.validate("Traceback", data).run()）
        """
        self.pending_model = model
        self.pending_data = data
        return self

    def run(self):
        """
        执行校验逻辑，返回最终字符串结果（校验入口方法）
        :return: 拼接后的错误信息字符串（无错误返回空字符串）
        """
        # 检查是否已通过validate设置待校验参数
        if self.pending_model is None or self.pending_data is None:
            return "请先调用validate(model, data)方法设置待校验参数"

        model = self.pending_model
        data = self.pending_data

        # 检查该model是否已注册规则类
        if model not in self.model_rule_map:
            # 无对应规则，默认校验通过
            self._reset_pending_params()  # 重置缓存参数
            return ""

        # 获取规则类和注册时传入的额外参数
        rule_class, rule_kwargs = self.model_rule_map[model]
        try:
            rule_instance = rule_class()  # 实例化规则类
        except Exception as e:
            error_msg = f"规则类{rule_class.__name__}实例化失败：{str(e)}"
            self._reset_pending_params()
            return error_msg

        # 自动识别所有以"check_"开头的校验方法
        validate_methods = [
            getattr(rule_instance, attr)
            for attr in dir(rule_instance)
            if attr.startswith("check_") and callable(getattr(rule_instance, attr))
        ]

        error_messages = []
        # 遍历执行所有校验方法（传递data + 额外参数）
        for method in validate_methods:
            try:
                # 校验方法接收 data 和 注册时配置的额外参数rule_kwargs
                error_msg = method(data, **rule_kwargs)
                # 收集非空字符串错误信息
                if error_msg and isinstance(error_msg, str):
                    error_messages.append(error_msg)
            except Exception as e:
                error_messages.append(f"{method.__name__}执行异常：{str(e)}")

        # 重置待校验参数，避免重复执行
        self._reset_pending_params()

        # 拼接并返回错误信息
        return "\n".join(error_messages)

    def _reset_pending_params(self):
        """重置缓存的待校验参数（私有辅助方法）"""
        self.pending_model = None
        self.pending_data = None


class ModelValidator_原始:
    """
    通用校验主类：支持直接注册规则类（无需提前实例化），自动管理与执行校验
    """
    def __init__(self):
        # 注册表：键为model名称，值为对应的模型规则类（非实例）
        self.model_rule_classes = {}

    def register_model_rules(self, model, rule_class):
        """
        直接注册模型规则类（无需实例化，传入类本身即可）
        :param model: 模型名称（字符串，如"user"、"order"）
        :param rule_class: 对应模型的规则类（如UserRules、OrderRules，无需实例化）
        """
        # 简单校验：确保传入的是类，且规则类可实例化
        if not isinstance(rule_class, type):
            raise TypeError(f"传入的{rule_class.__name__}必须是一个类（而非实例或其他类型）")
        self.model_rule_classes[model] = rule_class

    def validate(self, model, data, **kwargs):
        """
        执行校验，返回最终字符串结果
        :param model: 目标模型名称
        :param data: 待校验数据（任意类型）
        :param kwargs: 额外传递给校验方法的参数
        :return: 拼接后的错误信息字符串（无错误返回空字符串）
        """
        # 检查该model是否已注册规则类
        if model not in self.model_rule_classes:
            return ""

        # 自动实例化规则类（无需用户手动创建实例）
        rule_class = self.model_rule_classes[model]
        try:
            rule_instance = rule_class()  # 无参实例化（兼容绝大多数场景）
        except Exception as e:
            return f"规则类{rule_class.__name__}实例化失败：{str(e)}"

        # 自动识别所有以"check_"开头的校验方法（约定优于配置）
        validate_methods = [
            getattr(rule_instance, attr)
            for attr in dir(rule_instance)
            if attr.startswith("check_") and callable(getattr(rule_instance, attr))
        ]

        error_messages = []
        # 遍历所有校验方法，依次执行
        for method in validate_methods:
            try:
                # 执行单个校验方法，传递数据和额外参数
                error_msg = method(data, **kwargs)
                # 收集非空错误信息（确保返回值是字符串）
                if error_msg and isinstance(error_msg, str):
                    error_messages.append(error_msg)
            except Exception as e:
                # 捕获方法执行异常，转为友好错误信息
                error_messages.append(f"{method.__name__}执行异常：{str(e)}")

        # 拼接所有错误信息，返回最终字符串
        return "\n".join(error_messages)


# ------------------------------ 各Model的规则类（独立封装，无需实例化即可注册） ------------------------------
class UserRules:
    """
    User模型专属规则类：所有user相关校验规则封装在此类中
    无需提前实例化，直接传入register_model_rules即可
    """
    def check_username(self, data, min_len=2, max_len=10, **kwargs):
        """校验用户名：非空 + 长度限制"""
        username = data.get("username", "")
        if not username:
            return "用户名不能为空"
        if not (min_len <= len(username) <= max_len):
            return f"用户名长度必须在{min_len}-{max_len}之间"
        return ""

    def check_age(self, data, min_age=0, max_age=120, **kwargs):
        """校验年龄：数字类型 + 范围限制"""
        age = data.get("age", None)
        if not isinstance(age, (int, float)):
            return "年龄必须是数字类型"
        if not (min_age <= age <= max_age):
            return f"年龄必须在{min_age}-{max_age}之间"
        return ""

    def check_phone(self, data, **kwargs):
        """校验手机号格式：11位数字"""
        phone = data.get("phone", "")
        if not phone.isdigit() or len(phone) != 11:
            return "手机号必须是11位数字"
        return ""


class OrderRules:
    """
    Order模型专属规则类：所有order相关校验规则封装在此类中
    """
    def check_order_amount(self, data, min_amount=0.01, **kwargs):
        """校验订单金额：非负 + 最小值限制"""
        amount = data.get("amount", 0)
        if not isinstance(amount, (int, float)):
            return "订单金额必须是数字类型"
        if amount < min_amount:
            return f"订单金额不能低于{min_amount}元"
        return ""

    def check_order_no(self, data, **kwargs):
        """校验订单编号：非空 + ORD_前缀"""
        order_no = data.get("order_no", "")
        if not order_no:
            return "订单编号不能为空"
        if not order_no.startswith("ORD_"):
            return "订单编号必须以'ORD_'开头"
        return ""


# ------------------------------ 示例使用（核心：直接注册类，无需实例化） ------------------------------
if __name__ == "__main__":
    # 1. 创建通用校验主实例
    main_validator = ModelValidator()

    # 2. 直接注册规则类（无需先创建 user_rules = UserRules()，直接传UserRules类本身）
    main_validator.register_model_rules("user", UserRules)  # 关键优化：传入类，非实例
    main_validator.register_model_rules("order", OrderRules)

    # 3. 执行校验（用法与之前一致，无感知差异）
    # 测试无效用户数据
    invalid_user = {"username": "a", "age": 150, "phone": "1380013800"}
    user_result = main_validator.validate(
        model="user",
        data=invalid_user,
        min_len=2,
        max_age=120
    )
    print("【User模型校验结果】")
    print(user_result)
    print("-" * 60)

    # 测试无效订单数据
    invalid_order = {"amount": 0.005, "order_no": "123456789"}
    order_result = main_validator.validate(
        model="order",
        data=invalid_order,
        min_amount=0.01
    )
    print("【Order模型校验结果】")
    print(order_result)
    print("-" * 60)

    # 测试合法数据
    valid_user = {"username": "zhangsan", "age": 28, "phone": "13800138000"}
    valid_user_result = main_validator.validate(
        model="user",
        data=valid_user,
        min_len=2,
        max_age=120
    )
    print("【合法User校验结果】")
    print(f"校验通过（无错误）：{valid_user_result == ''}")
