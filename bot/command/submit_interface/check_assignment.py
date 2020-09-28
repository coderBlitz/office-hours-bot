import re
from datetime import datetime, timedelta
from discord import Message, Client

from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

import command
import mongo
from channels import ChannelAuthority
from roles import RoleAuthority


@command.command_class
class CheckAssignment(command.Command):
    __COMMAND_REGEX = r"!submit\s+check\s+(?P<assignment>w+)\s+(?P<file_name>(\w|[_]|[.])+)"
    __SUBMIT_SYSTEM_ADMINS = 'submit-system-admins'
    __SUBMIT_ASSIGNMENTS = 'submit-assignments'

    async def handle(self):
        ca: ChannelAuthority = ChannelAuthority(self.guild)
        ra: RoleAuthority = RoleAuthority(self.guild)

        match = re.match(self.__COMMAND_REGEX, self.message.content)
        if match:
            submit_col = mongo.db[self.__SUBMIT_SYSTEM_ADMINS]
            assignments = mongo.db[self.__SUBMIT_ASSIGNMENTS]

            # keep this for when we need to update on the server.
            if match.group('admin'):
                admin_match = submit_col.find_one({'username': match.group('admin')})
            else:
                admin_match = submit_col.find_one({})

            assignment_name = match.group('assign_name')
            dr: DeleteResult = assignments.delete_one({'name': assignment_name})
            if dr.deleted_count:
                await self.message.channel.send('Assignment {} has been removed'.format(assignment_name))
                self.client.submit_daemon.updated = True
            else:
                await self.message.channel.send('Assignment {} has not been removed'.format(assignment_name))

    @staticmethod
    async def is_invoked_by_message(message: Message, client: Client):
        if re.match(r"!submit\s+check\s+(?P<assign_name>\w+)", message.content):
            return True
        return False