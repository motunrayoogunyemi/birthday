class AppConfig:
    SECRET_KEY='O7hPqKchcAdlmbo'

class LiveConfig(AppConfig):
    SECRET_KEY='Hz_Vq0XyJUJ6rbo'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'ogunyemiimotunrayo@gmail.com'
    MAIL_PASSWORD = 'sarahlayo199'
    MAIL_USE_SSL = True
