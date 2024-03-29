# -*-coding:utf-8-*-
import mimetypes
from packaging import version
import re
import requests
import json
import os


class RocketException(Exception):
    pass


class RocketConnectionException(Exception):
    pass


class RocketAuthenticationException(Exception):
    pass


class RocketMissingParamException(Exception):
    pass


class RocketUnsuportedIntegrationType(Exception):
    pass


class RocketChatBase:
    API_path = "/api/v1/"

    def __init__(
        self,
        user=None,
        password=None,
        auth_token=None,
        user_id=None,
        server_url="http://127.0.0.1:3000",
        ssl_verify=True,
        proxies=None,
        timeout=30,
        session=None,
        client_certs=None,
    ):
        """Creates a RocketChat object and does login on the specified server"""
        self.headers = {}
        self.server_url = server_url
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.cert = client_certs
        self.timeout = timeout
        self.req = session or requests
        if user and password:
            self.login(user, password)  # skipcq: PTC-W1006
        if auth_token and user_id:
            self.headers["X-Auth-Token"] = auth_token
            self.headers["X-User-Id"] = user_id

    @staticmethod
    def __reduce_kwargs(kwargs):
        if "kwargs" in kwargs:
            for arg in kwargs["kwargs"].keys():
                kwargs[arg] = kwargs["kwargs"][arg]

            del kwargs["kwargs"]
        return kwargs

    def call_api_delete(self, method):
        url = self.server_url + self.API_path + method

        return self.req.delete(
            url,
            headers=self.headers,
            verify=self.ssl_verify,
            cert=self.cert,
            proxies=self.proxies,
            timeout=self.timeout,
        )

    def call_api_get(self, method, api_path=None, **kwargs):
        args = self.__reduce_kwargs(kwargs)
        if not api_path:
            api_path = self.API_path
        url = self.server_url + api_path + method
        # convert to key[]=val1&key[]=val2 for args like key=[val1, val2], else key=val
        params = "&".join(
            "&".join(i + "[]=" + j for j in args[i])
            if isinstance(args[i], list)
            else i + "=" + str(args[i])
            for i in args
        )
        return self.req.get(
            "%s?%s" % (url, params),
            headers=self.headers,
            verify=self.ssl_verify,
            cert=self.cert,
            proxies=self.proxies,
            timeout=self.timeout,
        )

    def call_api_post(self, method, files=None, use_json=None, **kwargs):
        reduced_args = self.__reduce_kwargs(kwargs)
        # Since pass is a reserved word in Python it has to be injected on the request dict
        # Some methods use pass (users.register) and others password (users.create)
        if "password" in reduced_args and method != "users.create":
            reduced_args["pass"] = reduced_args["password"]
            del reduced_args["password"]
        if use_json is None:
            # see https://requests.readthedocs.io/en/master/user/quickstart/#more-complicated-post-requests
            # > The json parameter is ignored if either data or files is passed.
            # If files are sent, json should not be used
            use_json = files is None
        if use_json:
            return self.req.post(
                self.server_url + self.API_path + method,
                json=reduced_args,
                files=files,
                headers=self.headers,
                verify=self.ssl_verify,
                cert=self.cert,
                proxies=self.proxies,
                timeout=self.timeout,
            )
        return self.req.post(
            self.server_url + self.API_path + method,
            data=reduced_args,
            files=files,
            headers=self.headers,
            verify=self.ssl_verify,
            cert=self.cert,
            proxies=self.proxies,
            timeout=self.timeout,
        )

    def call_api_put(self, method, files=None, use_json=None, **kwargs):
        reduced_args = self.__reduce_kwargs(kwargs)
        if use_json is None:
            # see https://requests.readthedocs.io/en/master/user/quickstart/#more-complicated-post-requests
            # > The json parameter is ignored if either data or files is passed.
            # If files are sent, json should not be used
            use_json = files is None
        if use_json:
            return self.req.put(
                self.server_url + self.API_path + method,
                json=reduced_args,
                files=files,
                headers=self.headers,
                verify=self.ssl_verify,
                cert=self.cert,
                proxies=self.proxies,
                timeout=self.timeout,
            )
        return self.req.put(
            self.server_url + self.API_path + method,
            data=reduced_args,
            files=files,
            headers=self.headers,
            verify=self.ssl_verify,
            cert=self.cert,
            proxies=self.proxies,
            timeout=self.timeout,
        )

    # Authentication

    def login(self, user, password):
        request_data = {"password": password}
        if re.match(
            r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
            user,
        ):
            request_data["user"] = user
        else:
            request_data["username"] = user
        login_request = self.req.post(
            self.server_url + self.API_path + "login",
            data=request_data,
            verify=self.ssl_verify,
            proxies=self.proxies,
            cert=self.cert,
            timeout=self.timeout,
        )
        if login_request.status_code == 401:
            raise RocketAuthenticationException()

        if (
            login_request.status_code == 200
            and login_request.json().get("status") == "success"
        ):
            self.headers["X-Auth-Token"] = (
                login_request.json().get("data").get("authToken")
            )
            self.headers["X-User-Id"] = login_request.json().get("data").get("userId")
            return login_request

        raise RocketConnectionException()

    def logout(self, **kwargs):
        """Invalidate your REST rocketchat_API authentication token."""
        return self.call_api_post("logout", kwargs=kwargs)

    def info(self, **kwargs):
        """Information about the Rocket.Chat server."""
        return self.call_api_get("info", api_path="/api/", kwargs=kwargs)


class RocketChatAssets(RocketChatBase):
    def assets_set_asset(self, asset_name, file, **kwargs):
        """Set an asset image by name."""
        server_info = self.info().json()
        content_type = mimetypes.MimeTypes().guess_type(file)

        file_name = asset_name
        if version.parse(server_info.get("info").get("version")) >= version.parse(
            "5.1"
        ):
            file_name = "asset"

        files = {
            file_name: (file, open(file, "rb"), content_type[0], {"Expires": "0"}),
        }

        return self.call_api_post(
            "assets.setAsset",
            kwargs=kwargs,
            assetName=asset_name,
            use_json=False,
            files=files,
        )

    def assets_unset_asset(self, asset_name):
        """Unset an asset by name"""
        return self.call_api_post("assets.unsetAsset", assetName=asset_name)


class RocketChatChannels(RocketChatBase):
    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.call_api_get("channels.list", kwargs=kwargs)

    def channels_list_joined(self, **kwargs):
        """Lists all of the channels the calling user has joined"""
        return self.call_api_get("channels.list.joined", kwargs=kwargs)

    def channels_info(self, room_id=None, channel=None, **kwargs):
        """Gets a channel's information."""
        if room_id:
            return self.call_api_get("channels.info", roomId=room_id, kwargs=kwargs)
        if channel:
            return self.call_api_get("channels.info", roomName=channel, kwargs=kwargs)
        raise RocketMissingParamException("room_id or channel required")

    def channels_history(self, room_id, **kwargs):
        """Retrieves the messages from a channel."""
        return self.call_api_get("channels.history", roomId=room_id, kwargs=kwargs)

    def channels_add_all(self, room_id, **kwargs):
        """Adds all of the users of the Rocket.Chat server to the channel."""
        return self.call_api_post("channels.addAll", roomId=room_id, kwargs=kwargs)

    def channels_add_moderator(self, room_id, user_id, **kwargs):
        """Gives the role of moderator for a user in the current channel."""
        return self.call_api_post(
            "channels.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_remove_moderator(self, room_id, user_id, **kwargs):
        """Removes the role of moderator from a user in the current channel."""
        return self.call_api_post(
            "channels.removeModerator", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_moderators(self, room_id=None, channel=None, **kwargs):
        """Lists all moderators of a channel."""
        if room_id:
            return self.call_api_get(
                "channels.moderators", roomId=room_id, kwargs=kwargs
            )
        if channel:
            return self.call_api_get(
                "channels.moderators", roomName=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or channel required")

    def channels_add_owner(self, room_id, user_id=None, username=None, **kwargs):
        """Gives the role of owner for a user in the current channel."""
        if user_id:
            return self.call_api_post(
                "channels.addOwner", roomId=room_id, userId=user_id, kwargs=kwargs
            )
        if username:
            return self.call_api_post(
                "channels.addOwner", roomId=room_id, username=username, kwargs=kwargs
            )
        raise RocketMissingParamException("userID or username required")

    def channels_remove_owner(self, room_id, user_id, **kwargs):
        """Removes the role of owner from a user in the current channel."""
        return self.call_api_post(
            "channels.removeOwner", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_add_leader(self, room_id, user_id, **kwargs):
        """Gives the role of Leader for a user in the current channel."""
        return self.call_api_post(
            "channels.addLeader", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_remove_leader(self, room_id, user_id, **kwargs):
        """Removes the role of Leader for a user in the current channel."""
        return self.call_api_post(
            "channels.removeLeader", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_archive(self, room_id, **kwargs):
        """Archives a channel."""
        return self.call_api_post("channels.archive", roomId=room_id, kwargs=kwargs)

    def channels_unarchive(self, room_id, **kwargs):
        """Unarchives a channel."""
        return self.call_api_post("channels.unarchive", roomId=room_id, kwargs=kwargs)

    def channels_close(self, room_id, **kwargs):
        """Removes the channel from the user's list of channels."""
        return self.call_api_post("channels.close", roomId=room_id, kwargs=kwargs)

    def channels_open(self, room_id, **kwargs):
        """Adds the channel back to the user's list of channels."""
        return self.call_api_post("channels.open", roomId=room_id, kwargs=kwargs)

    def channels_create(self, name, **kwargs):
        """Creates a new public channel, optionally including users."""
        return self.call_api_post("channels.create", name=name, kwargs=kwargs)

    def channels_get_integrations(self, room_id, **kwargs):
        """Retrieves the integrations which the channel has"""
        return self.call_api_get(
            "channels.getIntegrations", roomId=room_id, kwargs=kwargs
        )

    def channels_invite(self, room_id, user_id, **kwargs):
        """Adds a user to the channel."""
        return self.call_api_post(
            "channels.invite", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_join(self, room_id, join_code, **kwargs):
        """Joins yourself to the channel."""
        return self.call_api_post(
            "channels.join", roomId=room_id, joinCode=join_code, kwargs=kwargs
        )

    def channels_kick(self, room_id, user_id, **kwargs):
        """Removes a user from the channel."""
        return self.call_api_post(
            "channels.kick", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def channels_leave(self, room_id, **kwargs):
        """Causes the callee to be removed from the channel."""
        return self.call_api_post("channels.leave", roomId=room_id, kwargs=kwargs)

    def channels_rename(self, room_id, name, **kwargs):
        """Changes the name of the channel."""
        return self.call_api_post(
            "channels.rename", roomId=room_id, name=name, kwargs=kwargs
        )

    def channels_set_default(self, room_id, default, **kwargs):
        """Sets whether the channel is a default channel or not."""
        return self.call_api_post(
            "channels.setDefault",
            roomId=room_id,
            default=default,
            kwargs=kwargs,
        )

    def channels_set_description(self, room_id, description, **kwargs):
        """Sets the description for the channel."""
        return self.call_api_post(
            "channels.setDescription",
            roomId=room_id,
            description=description,
            kwargs=kwargs,
        )

    def channels_set_join_code(self, room_id, join_code, **kwargs):
        """Sets the code required to join the channel."""
        return self.call_api_post(
            "channels.setJoinCode", roomId=room_id, joinCode=join_code, kwargs=kwargs
        )

    def channels_set_read_only(self, room_id, read_only, **kwargs):
        """Sets whether the channel is read only or not."""
        return self.call_api_post(
            "channels.setReadOnly",
            roomId=room_id,
            readOnly=bool(read_only),
            kwargs=kwargs,
        )

    def channels_set_topic(self, room_id, topic, **kwargs):
        """Sets the topic for the channel."""
        return self.call_api_post(
            "channels.setTopic", roomId=room_id, topic=topic, kwargs=kwargs
        )

    def channels_set_type(self, room_id, a_type, **kwargs):
        """Sets the type of room this channel should be. The type of room this channel should be, either c or p."""
        return self.call_api_post(
            "channels.setType", roomId=room_id, type=a_type, kwargs=kwargs
        )

    def channels_set_announcement(self, room_id, announcement, **kwargs):
        """Sets the announcement for the channel."""
        return self.call_api_post(
            "channels.setAnnouncement",
            roomId=room_id,
            announcement=announcement,
            kwargs=kwargs,
        )

    def channels_set_custom_fields(self, rid, custom_fields):
        """Sets the custom fields for the channel."""
        return self.call_api_post(
            "channels.setCustomFields", roomId=rid, customFields=custom_fields
        )

    def channels_delete(self, room_id=None, channel=None, **kwargs):
        """Delete a public channel."""
        if room_id:
            return self.call_api_post("channels.delete", roomId=room_id, kwargs=kwargs)
        if channel:
            return self.call_api_post(
                "channels.delete", roomName=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or channel required")

    def channels_members(self, room_id=None, channel=None, **kwargs):
        """Lists all channel users."""
        if room_id:
            return self.call_api_get("channels.members", roomId=room_id, kwargs=kwargs)
        if channel:
            return self.call_api_get(
                "channels.members", roomName=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or channel required")

    def channels_roles(self, room_id=None, room_name=None, **kwargs):
        """Lists all user's roles in the channel."""
        if room_id:
            return self.call_api_get("channels.roles", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get(
                "channels.roles", roomName=room_name, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or room_name required")

    def channels_files(self, room_id=None, room_name=None, **kwargs):
        """Retrieves the files from a channel."""
        if room_id:
            return self.call_api_get("channels.files", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get(
                "channels.files", roomName=room_name, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or room_name required")

    def channels_get_all_user_mentions_by_channel(self, room_id, **kwargs):
        """Gets all the mentions of a channel."""
        return self.call_api_get(
            "channels.getAllUserMentionsByChannel", roomId=room_id, kwargs=kwargs
        )

    def channels_counters(self, room_id=None, room_name=None, **kwargs):
        """Gets counters for a channel."""
        if room_id:
            return self.call_api_get("channels.counters", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get(
                "channels.counters", roomName=room_name, kwargs=kwargs
            )
        raise RocketMissingParamException("room_id or room_name required")

    def channels_online(self, query):
        """Lists all online users of a channel if the channel's id is provided, otherwise it gets all online users of
        all channels."""
        return self.call_api_get("channels.online", query=json.dumps(query))


class RocketChatChat(RocketChatBase):
    def chat_post_message(self, text, room_id=None, channel=None, **kwargs):
        """Posts a new chat message."""
        if room_id:
            if text:
                return self.call_api_post(
                    "chat.postMessage", roomId=room_id, text=text, kwargs=kwargs
                )
            return self.call_api_post("chat.postMessage", roomId=room_id, kwargs=kwargs)
        if channel:
            if text:
                return self.call_api_post(
                    "chat.postMessage", channel=channel, text=text, kwargs=kwargs
                )
            return self.call_api_post(
                "chat.postMessage", channel=channel, kwargs=kwargs
            )
        raise RocketMissingParamException("roomId or channel required")

    def chat_send_message(self, message):
        if "rid" in message:
            return self.call_api_post("chat.sendMessage", message=message)
        raise RocketMissingParamException("message.rid required")

    def chat_get_message(self, msg_id, **kwargs):
        return self.call_api_get("chat.getMessage", msgId=msg_id, kwargs=kwargs)

    def chat_pin_message(self, msg_id, **kwargs):
        return self.call_api_post("chat.pinMessage", messageId=msg_id, kwargs=kwargs)

    def chat_unpin_message(self, msg_id, **kwargs):
        return self.call_api_post("chat.unPinMessage", messageId=msg_id, kwargs=kwargs)

    def chat_star_message(self, msg_id, **kwargs):
        return self.call_api_post("chat.starMessage", messageId=msg_id, kwargs=kwargs)

    def chat_unstar_message(self, msg_id, **kwargs):
        return self.call_api_post("chat.unStarMessage", messageId=msg_id, kwargs=kwargs)

    def chat_delete(self, room_id, msg_id, **kwargs):
        """Deletes a chat message."""
        return self.call_api_post(
            "chat.delete", roomId=room_id, msgId=msg_id, kwargs=kwargs
        )

    def chat_update(self, room_id, msg_id, text, **kwargs):
        """Updates the text of the chat message."""
        return self.call_api_post(
            "chat.update", roomId=room_id, msgId=msg_id, text=text, kwargs=kwargs
        )

    def chat_react(self, msg_id, emoji="smile", **kwargs):
        """Updates the text of the chat message."""
        return self.call_api_post(
            "chat.react", messageId=msg_id, emoji=emoji, kwargs=kwargs
        )

    def chat_search(self, room_id, search_text, **kwargs):
        """Search for messages in a channel by id and text message."""
        return self.call_api_get(
            "chat.search", roomId=room_id, searchText=search_text, kwargs=kwargs
        )

    def chat_get_message_read_receipts(self, message_id, **kwargs):
        """Get Message Read Receipts"""
        return self.call_api_get(
            "chat.getMessageReadReceipts", messageId=message_id, kwargs=kwargs
        )

    def chat_get_starred_messages(self, room_id, **kwargs):
        """Retrieve starred messages."""
        return self.call_api_get(
            "chat.getStarredMessages", roomId=room_id, kwargs=kwargs
        )

    def chat_report_message(self, message_id, description, **kwargs):
        """Reports a message."""
        return self.call_api_post(
            "chat.reportMessage",
            messageId=message_id,
            description=description,
            kwargs=kwargs,
        )

    def chat_follow_message(self, mid, **kwargs):
        """Follows a chat message to the message's channel."""
        return self.call_api_post("chat.followMessage", mid=mid, kwargs=kwargs)


class RocketChatGroups(RocketChatBase):
    def groups_list_all(self, **kwargs):
        """
        List all the private groups on the server.
        The calling user must have the 'view-room-administration' right
        """
        return self.call_api_get("groups.listAll", kwargs=kwargs)

    def groups_list(self, **kwargs):
        """List the private groups the caller is part of."""
        return self.call_api_get("groups.list", kwargs=kwargs)

    def groups_history(self, room_id, **kwargs):
        """Retrieves the messages from a private group."""
        return self.call_api_get("groups.history", roomId=room_id, kwargs=kwargs)

    def groups_add_moderator(self, room_id, user_id, **kwargs):
        """Gives the role of moderator for a user in the current groups."""
        return self.call_api_post(
            "groups.addModerator", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_remove_moderator(self, room_id, user_id, **kwargs):
        """Removes the role of moderator from a user in the current groups."""
        return self.call_api_post(
            "groups.removeModerator", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_moderators(self, room_id=None, group=None, **kwargs):
        """Lists all moderators of a group."""
        if room_id:
            return self.call_api_get("groups.moderators", roomId=room_id, kwargs=kwargs)
        if group:
            return self.call_api_get("groups.moderators", roomName=group, kwargs=kwargs)
        raise RocketMissingParamException("room_id or group required")

    def groups_add_owner(self, room_id, user_id, **kwargs):
        """Gives the role of owner for a user in the current Group."""
        return self.call_api_post(
            "groups.addOwner", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_remove_owner(self, room_id, user_id, **kwargs):
        """Removes the role of owner from a user in the current Group."""
        return self.call_api_post(
            "groups.removeOwner", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_archive(self, room_id, **kwargs):
        """Archives a private group, only if you're part of the group."""
        return self.call_api_post("groups.archive", roomId=room_id, kwargs=kwargs)

    def groups_unarchive(self, room_id, **kwargs):
        """Unarchives a private group."""
        return self.call_api_post("groups.unarchive", roomId=room_id, kwargs=kwargs)

    def groups_close(self, room_id, **kwargs):
        """Removes the private group from the user's list of groups, only if you're part of the group."""
        return self.call_api_post("groups.close", roomId=room_id, kwargs=kwargs)

    def groups_create(self, name, **kwargs):
        """Creates a new private group, optionally including users, only if you're part of the group."""
        return self.call_api_post("groups.create", name=name, kwargs=kwargs)

    def groups_get_integrations(self, room_id, **kwargs):
        """Retrieves the integrations which the group has"""
        return self.call_api_get(
            "groups.getIntegrations", roomId=room_id, kwargs=kwargs
        )

    def groups_info(self, room_id=None, room_name=None, **kwargs):
        """GRetrieves the information about the private group, only if you're part of the group."""
        if room_id:
            return self.call_api_get("groups.info", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get("groups.info", roomName=room_name, kwargs=kwargs)
        raise RocketMissingParamException("room_id or roomName required")

    def groups_invite(self, room_id, user_id, **kwargs):
        """Adds a user to the private group."""
        return self.call_api_post(
            "groups.invite", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_kick(self, room_id, user_id, **kwargs):
        """Removes a user from the private group."""
        return self.call_api_post(
            "groups.kick", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_leave(self, room_id, **kwargs):
        """Causes the callee to be removed from the private group, if they're part of it and are not the last owner."""
        return self.call_api_post("groups.leave", roomId=room_id, kwargs=kwargs)

    def groups_open(self, room_id, **kwargs):
        """Adds the private group back to the user's list of private groups."""
        return self.call_api_post("groups.open", roomId=room_id, kwargs=kwargs)

    def groups_rename(self, room_id, name, **kwargs):
        """Changes the name of the private group."""
        return self.call_api_post(
            "groups.rename", roomId=room_id, name=name, kwargs=kwargs
        )

    def groups_set_announcement(self, room_id, announcement, **kwargs):
        """Sets the announcement for the private group."""
        return self.call_api_post(
            "groups.setAnnouncement",
            roomId=room_id,
            announcement=announcement,
            kwargs=kwargs,
        )

    def groups_set_description(self, room_id, description, **kwargs):
        """Sets the description for the private group."""
        return self.call_api_post(
            "groups.setDescription",
            roomId=room_id,
            description=description,
            kwargs=kwargs,
        )

    def groups_set_read_only(self, room_id, read_only, **kwargs):
        """Sets whether the group is read only or not."""
        return self.call_api_post(
            "groups.setReadOnly",
            roomId=room_id,
            readOnly=bool(read_only),
            kwargs=kwargs,
        )

    def groups_set_topic(self, room_id, topic, **kwargs):
        """Sets the topic for the private group."""
        return self.call_api_post(
            "groups.setTopic", roomId=room_id, topic=topic, kwargs=kwargs
        )

    def groups_set_type(self, room_id, a_type, **kwargs):
        """Sets the type of room this group should be. The type of room this channel should be, either c or p."""
        return self.call_api_post(
            "groups.setType", roomId=room_id, type=a_type, kwargs=kwargs
        )

    def groups_set_custom_fields(
        self, custom_fields, room_id=None, room_name=None, **kwargs
    ):
        if room_id:
            return self.call_api_post(
                "groups.setCustomFields",
                roomId=room_id,
                customFields=custom_fields,
                kwargs=kwargs,
            )
        if room_name:
            return self.call_api_post(
                "groups.setCustomFields",
                roomName=room_name,
                customFields=custom_fields,
                kwargs=kwargs,
            )
        raise RocketMissingParamException("room_id or room_name required")

    def groups_delete(self, room_id=None, group=None, **kwargs):
        """Delete a private group."""
        if room_id:
            return self.call_api_post("groups.delete", roomId=room_id, kwargs=kwargs)
        if group:
            return self.call_api_post("groups.delete", roomName=group, kwargs=kwargs)
        raise RocketMissingParamException("room_id or group required")

    def groups_members(self, room_id=None, group=None, **kwargs):
        """Lists all group users."""
        if room_id:
            return self.call_api_get("groups.members", roomId=room_id, kwargs=kwargs)
        if group:
            return self.call_api_get("groups.members", roomName=group, kwargs=kwargs)
        raise RocketMissingParamException("room_id or group required")

    def groups_roles(self, room_id=None, room_name=None, **kwargs):
        """Lists all user's roles in the private group."""
        if room_id:
            return self.call_api_get("groups.roles", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get("groups.roles", roomName=room_name, kwargs=kwargs)
        raise RocketMissingParamException("room_id or room_name required")

    def groups_files(self, room_id=None, room_name=None, **kwargs):
        """Retrieves the files from a private group."""
        if room_id:
            return self.call_api_get("groups.files", roomId=room_id, kwargs=kwargs)
        if room_name:
            return self.call_api_get("groups.files", roomName=room_name, kwargs=kwargs)
        raise RocketMissingParamException("room_id or room_name required")

    def groups_add_leader(self, room_id, user_id, **kwargs):
        """Gives the role of Leader for a user in the current group."""
        return self.call_api_post(
            "groups.addLeader", roomId=room_id, userId=user_id, kwargs=kwargs
        )

    def groups_remove_leader(self, room_id, user_id, **kwargs):
        """Removes the role of Leader for a user in the current group."""
        return self.call_api_post(
            "groups.removeLeader", roomId=room_id, userId=user_id, kwargs=kwargs
        )


class RocketChatIM(RocketChatBase):
    def im_list(self, **kwargs):
        """List the private im chats for logged user"""
        return self.call_api_get("im.list", kwargs=kwargs)

    def im_list_everyone(self, **kwargs):
        """List all direct message the caller in the server."""
        return self.call_api_get("im.list.everyone", kwargs=kwargs)

    def im_history(self, room_id, **kwargs):
        """Retrieves the history for a private im chat"""
        return self.call_api_get("im.history", roomId=room_id, kwargs=kwargs)

    def im_create(self, username, **kwargs):
        """Create a direct message session with another user."""
        return self.call_api_post("im.create", username=username, kwargs=kwargs)

    def im_create_multiple(self, usernames, **kwargs):
        """Create a direct message session with one or more users."""
        return self.call_api_post(
            "im.create", usernames=",".join(usernames), kwargs=kwargs
        )

    def im_open(self, room_id, **kwargs):
        """Adds the direct message back to the user's list of direct messages."""
        return self.call_api_post("im.open", roomId=room_id, kwargs=kwargs)

    def im_close(self, room_id, **kwargs):
        """Removes the direct message from the user's list of direct messages."""
        return self.call_api_post("im.close", roomId=room_id, kwargs=kwargs)

    def im_members(self, room_id):
        """Retrieves members of a direct message."""
        return self.call_api_get("im.members", roomId=room_id)

    def im_messages(self, room_id=None, username=None):
        """Retrieves direct messages from the server by username"""
        if room_id:
            return self.call_api_get("im.messages", roomId=room_id)

        if username:
            return self.call_api_get("im.messages", username=username)

        raise RocketMissingParamException("roomId or username required")

    def im_messages_others(self, room_id, **kwargs):
        """Retrieves the messages from any direct message in the server"""
        return self.call_api_get("im.messages.others", roomId=room_id, kwargs=kwargs)

    def im_set_topic(self, room_id, topic, **kwargs):
        """Sets the topic for the direct message"""
        return self.call_api_post(
            "im.setTopic", roomId=room_id, topic=topic, kwargs=kwargs
        )

    def im_files(self, room_id=None, user_name=None, **kwargs):
        """Retrieves the files from a direct message."""
        if room_id:
            return self.call_api_get("im.files", roomId=room_id, kwargs=kwargs)
        if user_name:
            return self.call_api_get("im.files", username=user_name, kwargs=kwargs)
        raise RocketMissingParamException("roomId or username required")

    def im_counters(self, room_id, user_name=None):
        """Gets counters of direct messages."""
        if user_name:
            return self.call_api_get("im.counters", roomId=room_id, username=user_name)
        return self.call_api_get("im.counters", roomId=room_id)


class RocketChatIntegrations(RocketChatBase):
    # pylint: disable=too-many-arguments
    def integrations_create(
        self,
        integrations_type,
        name,
        enabled,
        username,
        channel,
        script_enabled,
        event=None,
        urls=None,
        **kwargs
    ):
        """Creates an integration."""
        if integrations_type == "webhook-outgoing":
            return self.call_api_post(
                "integrations.create",
                type=integrations_type,
                name=name,
                enabled=enabled,
                event=event,
                urls=urls,
                username=username,
                channel=channel,
                scriptEnabled=script_enabled,
                kwargs=kwargs,
            )
        elif integrations_type == "webhook-incoming":
            return self.call_api_post(
                "integrations.create",
                type=integrations_type,
                name=name,
                enabled=enabled,
                username=username,
                channel=channel,
                scriptEnabled=script_enabled,
                kwargs=kwargs,
            )
        else:
            raise RocketUnsuportedIntegrationType()

    def integrations_get(self, integration_id, **kwargs):
        """Retrieves an integration by id."""
        return self.call_api_get(
            "integrations.get", integrationId=integration_id, kwargs=kwargs
        )

    def integrations_history(self, integration_id, **kwargs):
        """Lists all history of the specified integration."""
        return self.call_api_get(
            "integrations.history", id=integration_id, kwargs=kwargs
        )

    def integrations_list(self, **kwargs):
        """Lists all of the integrations on the server."""
        return self.call_api_get("integrations.list", kwargs=kwargs)

    def integrations_remove(self, integrations_type, integration_id, **kwargs):
        """Removes an integration from the server."""
        return self.call_api_post(
            "integrations.remove",
            type=integrations_type,
            integrationId=integration_id,
            kwargs=kwargs,
        )

    def integrations_update(
        self,
        integrations_type,
        name,
        enabled,
        username,
        channel,
        script_enabled,
        integration_id,
        **kwargs
    ):
        """Updates an existing integration."""
        return self.call_api_put(
            "integrations.update",
            type=integrations_type,
            name=name,
            enabled=enabled,
            username=username,
            channel=channel,
            scriptEnabled=script_enabled,
            integrationId=integration_id,
            kwargs=kwargs,
        )


class RocketChatInvites(RocketChatBase):
    def find_or_create_invite(self, rid, days, max_uses):
        """
        Creates or return an existing invite with the specified parameters.
        Requires the create-invite-links permission
        """
        return self.call_api_post(
            "findOrCreateInvite", rid=rid, days=days, maxUses=max_uses
        )

    def list_invites(self, **kwargs):
        """Lists all of the invites on the server. Requires the create-invite-links permission."""
        return self.call_api_get("listInvites", kwargs=kwargs)


class RocketChatLivechat(RocketChatBase):
    def livechat_rooms(self, **kwargs):
        """Retrieves a list of livechat rooms."""
        return self.call_api_get("livechat/rooms", kwargs=kwargs)

    def livechat_inquiries_list(self, **kwargs):
        """Lists all of the open livechat inquiries."""
        return self.call_api_get("livechat/inquiries.list", kwargs=kwargs)

    def livechat_inquiries_take(self, inquiry_id, **kwargs):
        """Takes an open inquiry."""
        return self.call_api_post(
            "livechat/inquiries.take", inquiryId=inquiry_id, kwargs=kwargs
        )

    def livechat_get_users(self, user_type, **kwargs):
        """Get a list of agents or managers."""
        return self.call_api_get("livechat/users/{}".format(user_type), kwargs=kwargs)

    def livechat_create_user(self, user_type, **kwargs):
        """Register a new agent or manager."""
        return self.call_api_post("livechat/users/{}".format(user_type), kwargs=kwargs)

    def livechat_get_user(self, user_type, user_id, **kwargs):
        """Get info about an agent or manager."""
        return self.call_api_get(
            "livechat/users/{}/{}".format(user_type, user_id), kwargs=kwargs
        )

    def livechat_delete_user(self, user_type, user_id):
        """Removes an agent or manager."""
        return self.call_api_delete("livechat/users/{}/{}".format(user_type, user_id))

    def livechat_register_visitor(self, token, **kwargs):
        """Register a new Livechat visitor."""
        if "visitor" not in kwargs:
            kwargs["visitor"] = {}
        kwargs["visitor"]["token"] = token
        return self.call_api_post("livechat/visitor", kwargs=kwargs)

    def livechat_get_visitor(self, token):
        """Retrieve a visitor data."""
        return self.call_api_get("livechat/visitor/{}".format(token))

    def livechat_room(self, token, **kwargs):
        """Get the Livechat room data or open a new room."""
        return self.call_api_get("livechat/room/", token=token, kwargs=kwargs)

    def livechat_message(self, token, rid, msg, **kwargs):
        """Send a new Livechat message."""
        return self.call_api_post(
            "livechat/message", token=token, rid=rid, msg=msg, kwargs=kwargs
        )

    def livechat_messages_history(self, rid, token, **kwargs):
        """Load Livechat messages history."""
        return self.call_api_get(
            "livechat/messages.history/{}".format(rid), token=token, kwargs=kwargs
        )


class RocketChatMiscellaneous(RocketChatBase):
    # Miscellaneous information
    def directory(self, query, **kwargs):
        """Search by users or channels on all server."""
        if isinstance(query, dict):
            query = str(query).replace("'", '"')

        return self.call_api_get("directory", query=query, kwargs=kwargs)

    def spotlight(self, query, **kwargs):
        """Searches for users or rooms that are visible to the user."""
        return self.call_api_get("spotlight", query=query, kwargs=kwargs)


class RocketChatPermissions(RocketChatBase):
    def permissions_list_all(self, **kwargs):
        """Returns all permissions from the server."""
        return self.call_api_get("permissions.listAll", kwargs=kwargs)


class RocketChatRoles(RocketChatBase):
    def roles_list(self, **kwargs):
        """Gets all the roles in the system."""
        return self.call_api_get("roles.list", kwargs=kwargs)

    def roles_create(self, name, **kwargs):
        """Create a new role in the system."""
        return self.call_api_post("roles.create", name=name, kwargs=kwargs)

    def roles_add_user_to_role(self, role_name, username, **kwargs):
        """Assign a role to a user. Optionally, you can set this role to a room."""
        return self.call_api_post(
            "roles.addUserToRole", roleName=role_name, username=username, kwargs=kwargs
        )

    def roles_remove_user_from_role(self, role_name, username, **kwargs):
        """Remove a role from a user. Optionally, you can unset this role for a specified scope."""
        return self.call_api_post(
            "roles.removeUserFromRole",
            roleName=role_name,
            username=username,
            kwargs=kwargs,
        )

    def roles_get_users_in_role(self, role, **kwargs):
        """Gets the users that belongs to a role. It supports the Offset and Count Only."""
        return self.call_api_get("roles.getUsersInRole", role=role, kwargs=kwargs)

    def roles_sync(self, updated_since):
        """Gets all the roles in the system which are updated after a given date."""
        return self.call_api_get("roles.sync", updatedSince=updated_since)


class RocketChatRooms(RocketChatBase):
    def rooms_upload(self, rid, file, **kwargs):
        """Post a message with attached file to a dedicated room."""
        files = {
            "file": (
                os.path.basename(file),
                open(file, "rb"),
                mimetypes.guess_type(file)[0],
            ),
        }
        return self.call_api_post(
            "rooms.upload/" + rid, kwargs=kwargs, use_json=False, files=files
        )

    def rooms_get(self, **kwargs):
        """Get all opened rooms for this user."""
        return self.call_api_get("rooms.get", kwargs=kwargs)

    def rooms_clean_history(self, room_id, latest, oldest, **kwargs):
        """Cleans up a room, removing messages from the provided time range."""
        return self.call_api_post(
            "rooms.cleanHistory",
            roomId=room_id,
            latest=latest,
            oldest=oldest,
            kwargs=kwargs,
        )

    def rooms_favorite(self, room_id=None, room_name=None, favorite=True):
        """Favorite or unfavorite room."""
        if room_id is not None:
            return self.call_api_post(
                "rooms.favorite", roomId=room_id, favorite=favorite
            )
        if room_name is not None:
            return self.call_api_post(
                "rooms.favorite", roomName=room_name, favorite=favorite
            )
        raise RocketMissingParamException("room_id or roomName required")

    def rooms_info(self, room_id=None, room_name=None):
        """Retrieves the information about the room."""
        if room_id is not None:
            return self.call_api_get("rooms.info", roomId=room_id)
        if room_name is not None:
            return self.call_api_get("rooms.info", roomName=room_name)
        raise RocketMissingParamException("room_id or roomName required")

    def rooms_admin_rooms(self, **kwargs):
        """Retrieves all rooms (requires the view-room-administration permission)."""
        return self.call_api_get("rooms.adminRooms", kwargs=kwargs)

    def rooms_create_discussion(self, prid, t_name, **kwargs):
        """
        Creates a new discussion for room. It requires at least one of the
        following permissions: start-discussion OR start-discussion-other-user,
        AND must be with the following setting enabled: Discussion_enabled.
        """
        return self.call_api_post(
            "rooms.createDiscussion", prid=prid, t_name=t_name, kwargs=kwargs
        )


class RocketChatSettings(RocketChatBase):
    def settings_get(self, _id, **kwargs):
        """Gets the setting for the provided _id."""
        return self.call_api_get("settings/" + _id, kwargs=kwargs)

    def settings_update(self, _id, value, **kwargs):
        """Updates the setting for the provided _id."""
        return self.call_api_post("settings/" + _id, value=value, kwargs=kwargs)

    def settings(self, **kwargs):
        """List all private settings."""
        return self.call_api_get("settings", kwargs=kwargs)

    def settings_public(self, **kwargs):
        """List all private settings."""
        return self.call_api_get("settings.public", kwargs=kwargs)

    def settings_oauth(self, **kwargs):
        """List all OAuth services."""
        return self.call_api_get("settings.oauth", kwargs=kwargs)

    def settings_addcustomoauth(self, name, **kwargs):
        """Add a new custom OAuth service with the provided name."""
        return self.call_api_post("settings.addCustomOAuth", name=name, kwargs=kwargs)

    def service_configurations(self, **kwargs):
        """List all service configurations."""
        return self.call_api_get("service.configurations", kwargs=kwargs)


class RocketChatStatistics(RocketChatBase):
    def statistics(self, **kwargs):
        """Retrieves the current statistics"""
        return self.call_api_get("statistics", kwargs=kwargs)

    def statistics_list(self, **kwargs):
        """Selectable statistics about the Rocket.Chat server."""
        return self.call_api_get("statistics.list", kwargs=kwargs)


class RocketChatSubscriptions(RocketChatBase):
    def subscriptions_get(self, **kwargs):
        """Get all subscriptions."""
        return self.call_api_get("subscriptions.get", kwargs=kwargs)

    def subscriptions_get_one(self, room_id, **kwargs):
        """Get the subscription by room id."""
        return self.call_api_get("subscriptions.getOne", roomId=room_id, kwargs=kwargs)

    def subscriptions_unread(self, room_id, **kwargs):
        """Mark messages as unread by roomId or from a message"""
        return self.call_api_post("subscriptions.unread", roomId=room_id, kwargs=kwargs)

    def subscriptions_read(self, rid, **kwargs):
        """Mark room as read"""
        return self.call_api_post("subscriptions.read", rid=rid, kwargs=kwargs)


class RocketChatTeams(RocketChatBase):
    def teams_create(self, name, team_type, **kwargs):
        """Creates a new team. Requires create-team permission."""
        return self.call_api_post(
            "teams.create", name=name, type=team_type, kwargs=kwargs
        )


class RocketChatUsers(RocketChatBase):
    def me(self, **kwargs):
        """Displays information about the authenticated user."""
        return self.call_api_get("me", kwargs=kwargs)

    def users_info(self, user_id=None, username=None, **kwargs):
        """Gets a user's information, limited to the caller's permissions."""
        if user_id:
            return self.call_api_get("users.info", userId=user_id, kwargs=kwargs)
        if username:
            return self.call_api_get("users.info", username=username, kwargs=kwargs)
        raise RocketMissingParamException("userID or username required")

    def users_list(self, **kwargs):
        """All of the users and their information, limited to permissions."""
        return self.call_api_get("users.list", kwargs=kwargs)

    def users_get_presence(self, user_id=None, username=None, **kwargs):
        """Gets the online presence of the a user."""
        if user_id:
            return self.call_api_get("users.getPresence", userId=user_id, kwargs=kwargs)
        if username:
            return self.call_api_get(
                "users.getPresence", username=username, kwargs=kwargs
            )
        raise RocketMissingParamException("userID or username required")

    def users_create(self, email, name, password, username, **kwargs):
        """Creates a user"""
        return self.call_api_post(
            "users.create",
            email=email,
            name=name,
            password=password,
            username=username,
            kwargs=kwargs,
        )

    def users_delete(self, user_id, **kwargs):
        """Deletes a user"""
        return self.call_api_post("users.delete", userId=user_id, **kwargs)

    def users_register(self, email, name, password, username, **kwargs):
        """Register a new user."""
        return self.call_api_post(
            "users.register",
            email=email,
            name=name,
            password=password,
            username=username,
            kwargs=kwargs,
        )

    def users_get_avatar(self, user_id=None, username=None, **kwargs):
        """Gets the URL for a user's avatar."""
        if user_id:
            response = self.call_api_get(
                "users.getAvatar", userId=user_id, kwargs=kwargs
            )
        elif username:
            response = self.call_api_get(
                "users.getAvatar", username=username, kwargs=kwargs
            )
        else:
            raise RocketMissingParamException("userID or username required")

        # If Accounts_AvatarBlockUnauthorizedAccess is set, we need to provide the Token as cookies
        if response.status_code == 403:
            return self.req.get(
                response.url,
                cert=self.cert,
                cookies={
                    "rc_uid": self.headers.get("X-User-Id"),
                    "rc_token": self.headers.get("X-Auth-Token"),
                },
            )
        return response

    def users_set_avatar(self, avatar_url, **kwargs):
        """Set a user's avatar"""
        if avatar_url.startswith("http://") or avatar_url.startswith("https://"):
            return self.call_api_post(
                "users.setAvatar", avatarUrl=avatar_url, kwargs=kwargs
            )

        avatar_file = {
            "image": (
                os.path.basename(avatar_url),
                open(avatar_url, "rb"),
                mimetypes.guess_type(avatar_url)[0],
            ),
        }

        return self.call_api_post("users.setAvatar", files=avatar_file, kwargs=kwargs)

    def users_reset_avatar(self, user_id=None, username=None, **kwargs):
        """Reset a user's avatar"""
        if user_id:
            return self.call_api_post(
                "users.resetAvatar", userId=user_id, kwargs=kwargs
            )
        if username:
            return self.call_api_post(
                "users.resetAvatar", username=username, kwargs=kwargs
            )
        raise RocketMissingParamException("userID or username required")

    def users_create_token(self, user_id=None, username=None, **kwargs):
        """Create a user authentication token."""
        if user_id:
            return self.call_api_post(
                "users.createToken", userId=user_id, kwargs=kwargs
            )
        if username:
            return self.call_api_post(
                "users.createToken", username=username, kwargs=kwargs
            )
        raise RocketMissingParamException("userID or username required")

    def users_update(self, user_id, **kwargs):
        """Update an existing user."""
        return self.call_api_post("users.update", userId=user_id, data=kwargs)

    def users_set_active_status(self, user_id, active_status, **kwargs):
        """Update user active status."""
        return self.call_api_post(
            "users.setActiveStatus",
            userId=user_id,
            activeStatus=active_status,
            kwargs=kwargs,
        )

    def users_forgot_password(self, email, **kwargs):
        """Send email to reset your password."""
        return self.call_api_post("users.forgotPassword", email=email, data=kwargs)

    def users_get_preferences(self, **kwargs):
        """Gets all preferences of user."""
        return self.call_api_get("users.getPreferences", kwargs=kwargs)

    def users_set_preferences(self, user_id, data, **kwargs):
        """Set user's preferences."""
        return self.call_api_post(
            "users.setPreferences", userId=user_id, data=data, kwargs=kwargs
        )

    def users_set_status(self, message, **kwargs):
        """Sets a user Status when the status message and state is given."""
        return self.call_api_post("users.setStatus", message=message, kwargs=kwargs)


class RocketChatVideConferences(RocketChatBase):
    def update_jitsi_timeout(self, room_id, **kwargs):
        """Updates the timeout of Jitsi video conference in a channel."""
        return self.call_api_post(
            "video-conference/jitsi.update-timeout", roomId=room_id, kwargs=kwargs
        )

class RocketChat(
    RocketChatUsers,
    RocketChatChat,
    RocketChatChannels,
    RocketChatGroups,
    RocketChatIM,
    RocketChatIntegrations,
    RocketChatStatistics,
    RocketChatMiscellaneous,
    RocketChatSettings,
    RocketChatRooms,
    RocketChatSubscriptions,
    RocketChatAssets,
    RocketChatPermissions,
    RocketChatInvites,
    RocketChatVideConferences,
    RocketChatLivechat,
    RocketChatTeams,
    RocketChatRoles,
):
    pass
