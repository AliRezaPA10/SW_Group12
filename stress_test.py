from locust import HttpUser, TaskSet, between, task
from locust import LoadTestShape
import json
from requests.exceptions import JSONDecodeError


class UserTasks(TaskSet):
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
                        "username": "Armantest",
                        "email": "Armantest@gmail.com"
                    }
                }
                update_response = self.client.put("/api/v1/user/9", headers=headers, json=update_info)
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
                    "message": "Hellloooo!!!!!!",
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
                    "message": "Hiiii Thereeeee!!!!!",
                }
            }
            update_post_response = self.client.put(f"/api/v1/post/{self.post_id}", headers=headers, json=update_data)
            if update_post_response.status_code != 200:
                print("Failed to update post!")
            # Get updated post
            edited_post_response = self.client.get(f"/api/v1/post/{self.post_id}", headers=headers)
            if edited_post_response.status_code != 200:
                print("Failed to fetch updated post!")
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
                "name": "[[[[[ GTA V ]]]]]",
                "description": "Just for GTA fans!!!",
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
                    "title": "Conversation from API",
                    "message": "First message from API",
                    "recipient": [guid]
                }
                message_response = self.client.post("/api/v1/mail", headers=headers, json=message_data)
                if message_response.status_code != 200:
                    print("Failed to send message!")
                else:
                    tags_data = {"tags": ["CODE", "COMPUTER", "Work"]}
                    update_tags_response = self.client.put("/api/v1/mail/1/tags", headers=headers, json=tags_data)
                    if update_tags_response.status_code != 200:
                        print("Failed to update tags!")
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
                        "message": "Greate JOOOOOB!!!!!!!"
                    }
                }
                comment_response = self.client.post("/api/v1/comment", headers=headers, json=comment_data)
                if comment_response.status_code != 200:
                    print("Failed to add comment!")
            else:
                print("Failed to fetch post data!")
        except JSONDecodeError as e:
            print("Error decoding JSON response:", e)


class User(HttpUser):
    wait_time = between(0.5, 1.5)
    tasks = [UserTasks]
    host = "http://localhost/social-network/humhub"


class CustomShape(LoadTestShape):
    stages = [
        {"duration": 30, "users": 50, "spawn_rate": 10},
        {"duration": 60, "users": 150, "spawn_rate": 10},
        {"duration": 90, "users": 250, "spawn_rate": 10},
        {"duration": 120, "users": 350, "spawn_rate": 10},
        {"duration": 150, "users": 450, "spawn_rate": 10},
        {"duration": 180, "users": 550, "spawn_rate": 10},
        {"duration": 210, "users": 650, "spawn_rate": 10},
        {"duration": 240, "users": 750, "spawn_rate": 10},
        {"duration": 270, "users": 850, "spawn_rate": 10},
        {"duration": 300, "users": 1000, "spawn_rate": 10},
        {"duration": 330, "users": 500, "spawn_rate": 10},
        {"duration": 360, "users": 250, "spawn_rate": 10},
        {"duration": 390, "users": 100, "spawn_rate": 10},
        {"duration": 420, "users": 50, "spawn_rate": 10},
        {"duration": 450, "users": 10, "spawn_rate": 1},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
