from locust import HttpUser, task, between
import json
from requests.exceptions import JSONDecodeError


class HumHubUser(HttpUser):
    host = "http://localhost/social-network/humhub"
    wait_time = between(1, 3)
    post_id = None

    def on_start(self):
        self.token = self.login()

    def login(self):
        user_credentials = {
            "username": "ArmanMoradi",
            "password": "123456"
        }
        response = self.client.post("/api/v1/auth/login", json=user_credentials)
        if response.status_code == 200:
            return response.json()["auth_token"]
        else:
            print("Login failed!")
            return None

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(weight=1)
    def user_profile(self):
        if not self.token:
            print("No token found!")
            return
        try:
            headers = self.get_headers()
            profile_response = self.client.get("/api/v1/user/9", headers=headers)
            if profile_response.status_code != 200:
                print("Failed to fetch user profile!")
            else:
                update_info = {
                    "account": {
                        "username": "Arman22",
                        "email": "Arman2@gmail.com"
                    }
                }
                update_response = self.client.put("/api/v1/user/10", headers=headers, json=update_info)
                if update_response.status_code != 200:
                    print("Failed to update user profile!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)

    @task(weight=3)
    def create_and_update_post(self):
        if not self.token:
            print("No token found!")
            return
        try:
            headers = self.get_headers()
            post_data = {
                "data": {
                    "message": "Hello World!",
                    "content": {
                        "metadata": {
                            "visibility": 1,
                            "state": 1,
                            "archived": False,
                            "hidden": False,
                            "pinned": False,
                            "locked_comments": False
                        }
                    }
                }
            }
            create_post_response = self.client.post("/api/v1/post/container/1", headers=headers, json=post_data)
            if create_post_response.status_code != 200:
                print("Failed to create post!")
                return
            self.post_id = create_post_response.json()["id"]
            update_data = {
                "data": {
                    "message": "Updated message!"
                }
            }
            update_post_response = self.client.put(f"/api/v1/post/{self.post_id}", headers=headers, json=update_data)
            if update_post_response.status_code != 200:
                print("Failed to update post!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)

    @task(weight=2)
    def create_space_and_add_member(self):
        if not self.token:
            print("No token found!")
            return
        try:
            headers = self.get_headers()
            space_info = {
                "name": "DOTA 2 Room",
                "description": "Room for DOTA players",
                "visibility": 1,
                "join_policy": 1
            }
            space_response = self.client.post("/api/v1/space", headers=headers, json=space_info)
            if space_response.status_code == 200:
                space_id = space_response.json()["id"]
            else:
                print("Failed to create space!")
                return
            member_response = self.client.get("/api/v1/user/get-by-username?username=parizo", headers=headers)
            if member_response.status_code == 200:
                member_id = member_response.json()["id"]
                add_member_response = self.client.post(f"/api/v1/space/{space_id}/membership/{member_id}", headers=headers)
                if add_member_response.status_code != 200:
                    print("Failed to add member to space!")
                else:
                    role_data = {"role": "moderator"}
                    role_response = self.client.patch(f"/api/v1/space/{space_id}/membership/{member_id}/role", headers=headers, json=role_data)
                    if role_response.status_code != 200:
                        print("Failed to change user role!")
            else:
                print("Failed to fetch member!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)

    @task(weight=2)
    def create_and_send_message(self):
        if not self.token:
            print("No token found!")
            return
        try:
            headers = self.get_headers()
            user_response = self.client.get("/api/v1/user/5", headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                guid = user_data["guid"]
                message_data = {
                    "title": "Message from API",
                    "message": "Hello from API",
                    "recipient": [guid]
                }
                message_response = self.client.post("/api/v1/mail", headers=headers, json=message_data)
                if message_response.status_code == 200:
                    tags_data = {"tags": ["API", "Test", "Message"]}
                    update_tags_response = self.client.put("/api/v1/mail/1/tags", headers=headers, json=tags_data)
                    if update_tags_response.status_code != 200:
                        print("Failed to update tags!")
                else:
                    print("Failed to send message!")
            else:
                print("Failed to fetch user data!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)

    @task(weight=2)
    def add_comment(self):
        if not self.token:
            print("No token found!")
            return
        try:
            headers = self.get_headers()
            post_response = self.client.get(f"/api/v1/post/{self.post_id}", headers=headers)
            if post_response.status_code == 200:
                post_data = post_response.json()
                obj_model = post_data["content"]["metadata"]["object_model"]
                obj_id = post_data["content"]["metadata"]["object_id"]
                comment_data = {
                    "objectModel": obj_model,
                    "objectId": obj_id,
                    "Comment": {
                        "message": "Great job!"
                    }
                }
                comment_response = self.client.post("/api/v1/comment", headers=headers, json=comment_data)
                if comment_response.status_code != 200:
                    print("Failed to add comment!")
            else:
                print("Failed to fetch post data!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)
