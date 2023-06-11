# from talky.plugin import Plugin, register_plugin
# from talky.config import settings, logger

# from findmyorder import FindMyOrder

# class FindMyOrderPlugin(Plugin):
#     def __init__(self):
#         self.find_my_order = FindMyOrder()

#     async def start(self):
#         self.logger = logging.getLogger(name="FMO")
#         self.logger.info("Starting FindMyOrder service...")
#         self.find_my_order = FindMyOrder()
#         self.find_my_order.__init__()

#     async def stop(self):
#         self.logger.info("Stopping FindMyOrder service...")
#         self.find_my_order.close()

# @register_plugin
# class FindMyOrderPluginWrapper:
#     def __init__(self):
#         self.plugin = FindMyOrderPlugin()

#     async def start(self):
#         await self.plugin.start()

#     async def stop(self):
#         await self.plugin.stop()
