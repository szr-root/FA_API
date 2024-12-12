class CaseLogHandel:
    """日志处理的类"""

    def save_log(self, massage, level):
        """
        保存日志的方法
        :param massage: 日志内容
        :param level: 日志级别
        :return:
        """
        if not hasattr(self, 'log_data'):
            setattr(self, 'log_data', [])
        # 将日志保存到用来的log_data中
        getattr(self, 'log_data').append((level, massage))
        print((level, massage))

    def print_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'PRINT')

    def debug_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'DEBUG')

    def info_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'INFO')

    def error_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'ERROR')

    def warning_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'WARN')

    def critical_log(self, *args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'CRITICAL')


if __name__ == '__main__':
    log = CaseLogHandel()
    log.debug_log('日志', '1234567')
