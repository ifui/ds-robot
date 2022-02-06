from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.mail import MailSender
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify
import shutil

settings = get_project_settings()

jinjia = Environment(loader=FileSystemLoader(
    settings['BASE_PATH'] + '/robot/'))
template = jinjia.get_template('email.html')


class SendEmail:
    """
    发送通知邮件
    """

    def __init__(self, crawler):
        self.crawler = crawler
        self.mailer = MailSender().from_settings(settings)
        # 注册信号
        crawler.signals.connect(self.engine_stopped,
                                signal=signals.engine_stopped)

    @ classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # 爬虫结束时回调
    def engine_stopped(self):
        if self.crawler.stats.get_value('log_count/ERROR'):
            subject = self.crawler.spider.title + '采集失败通知'
        else:
            subject = self.crawler.spider.title + '采集成功通知'

        body = minify(template.render(data=self.crawler))

        return self.mailer.send(to=settings['TO_EMAIL'],
                                subject=subject,
                                body=body,
                                mimetype='text/html')


class ArchiveJob:
    """
    打包文件夹
    """

    def __init__(self, crawler):
        # 注册信号
        crawler.signals.connect(self.engine_stopped,
                                signal=signals.engine_stopped)

    @ classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # 爬虫结束时回调
    def engine_stopped(self):
        filename = settings['JOB_ID']
        file_path = settings['PUBLIC_PATH']
        archive_path = settings['ARCHIVE_PATH']
        shutil.make_archive(archive_path + '/' + filename, 'zip', file_path)
