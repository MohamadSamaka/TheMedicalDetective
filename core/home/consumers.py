from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json

# class Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # self.channel_name = self.scope['url_route']['kwags']['channel_name']
#         # self.channel_group_name
#         # self.accept()
#         # self.send(text_data=json.dumps({
#         #     'type': 'connnectoin_established',
#         #     'message':'You are now connected!'
#         #     })
#         # )
#         await self.send(text_data=json.dumps({
#             'type': 'connnectoin_established',
#             'message':'You are now connected!'
#             })
#         )
#         # await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def send_progress_update(self, event):
#         progress = event['progress']
#         await self.send(text_data=str(progress))

from asgiref.sync import async_to_sync



# class Consumer(WebsocketConsumer):
#     def connect(self):
#         self.group_name = "train"
#         async_to_sync(self.channel_layer.group_add)(
#             self.group_name,
#             self.channel_name
#         )
#         self.accept()

#     def send_progress_update(self, progress):

#         self.send(text_data=str(progress))








class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "train"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("admin disconnected")
        # Remove the client from the group "train" when the websocket connection is closed
        await self.channel_layer.group_discard("train", self.channel_name)



    async def progress_update(self, progress):
        await self.send(text_data=str(progress))

    async def form_validiation_result(self, validity):
        await self.send(text_data=str(validity))






# class Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data=json.dumps({
#             'hello': 'wrold!',
#         }))

#     async def send_progress_update(self, progress):
#         await self.send(text_data=str(progress))




















    # class Consumer(WebsocketConsumer):
    # def connect(self):

    #     self.accept()
    #     self.send(text_data=json.dumps({
    #         'hello': 'wrold!',
    #     }))

    # def send_progress_update(self, progress):
    #     # self.accept()
    #     self.send(text_data=str(progress))

    # # async def disconnect(self, close_code):
    # #     pass

    # # async def send_progress_update(self, event):
    # #     progress = event['progress']
    # #     await self.send(text_data=str(progress))
