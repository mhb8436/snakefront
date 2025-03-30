import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from main.models import Workflow
from main.tasks import serialize_workflow_statuses, serialize_runworkflow_statuses
from snakefront.settings import cfg
from asgiref.sync import sync_to_async
from api.models import RunWorkflow

def get_statuses(workflow_id):
    """Return a dictionary of workflow statuses on success. If the workflow
    doesn't exist, then return False and we disconnect from the socket.
    """
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        return {
            "statuses": serialize_workflow_statuses(workflow),
            "output": workflow.output,
            "error": workflow.error,
            "retval": workflow.retval,
        }
    except:
        return False

def get_runworkflow_statuses(workflow_id):
    try:
        print('workflow id', workflow_id)
        workflow = Workflow.objects.get(id=workflow_id)
        runworkflows = serialize_runworkflow_statuses(workflow)
        # runworkflows.sort(key=lambda x: x.id, reverse=True)
        
        return {
            "data": runworkflows,
            "output": workflow.output,
            "error": workflow.error,
            "retval": workflow.retval,
        }

    except:
        return False

async_get_statuses = sync_to_async(get_statuses, thread_sensitive=True)
async_get_runworkflow_statuses = sync_to_async(get_runworkflow_statuses, thread_sensitive=True)
 

class WorkflowConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.workflow_id = self.scope["path"].strip("/").split("/")[-1]
        print("websocket connect for workflow %s" % self.workflow_id)
        self.connected = True
        await self.channel_layer.group_add(self.workflow_id, self.channel_name)
        await self.accept()
        asyncio.create_task(self.update_workflow_status())

    async def update_workflow_status(self):
        while self.connected:
            await asyncio.sleep(cfg.WORKFLOW_UPDATE_SECONDS)

            status = "success"
            # data = await async_get_statuses(self.workflow_id)
            data = await async_get_runworkflow_statuses(self.workflow_id)
            if data == False:
                data = {
                    "message": "Workflow with id %s does not exist." % self.workflow_id
                }
                status = "error"
                self.connected = False

            await self.send_json(
                {"type": "websocket.send", "results": data, "status": status}
            )

    async def disconnect(self, close_code):
        self.connected = False
        await self.channel_layer.group_discard(self.workflow_id, self.channel_name)

    async def receive(self, text_data):
        print("receive", text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )
