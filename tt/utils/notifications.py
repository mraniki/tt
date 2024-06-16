# import apprise

# from tt.config import logger, settings


# class Notifier:
#     """
#     💬 Notification via Apprise.

#     """

#     def __init__(self):
#         logger.debug("Notifier initialized")
#         self.aobj = apprise.Apprise()

#         self.apprise_format = getattr(apprise.NotifyFormat, settings.apprise_format)
#         self.apprise_url = settings.apprise_url

#         self.aobj.add(self.apprise_url)

#     async def notify(self, msg):
#         await self.aobj.async_notify(body=msg, body_format=self.msg_format)
