
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bot.config import Config
from googleapiclient.errors import HttpError
import requests

class Blogger:
    def __init__(self, blogger_id, credentials_file="credentials.json"):
        self.blogger_id = blogger_id
        discoveryUrl = ('https://blogger.googleapis.com/$discovery/rest?version=v3')
        self.service = build(
            'blogger', 'v3', credentials=Credentials.from_authorized_user_file(credentials_file),
         discoveryServiceUrl=discoveryUrl)
        

    async def verify_credentials(self, blog_id):
        # sourcery skip: raise-specific-error
        try:
            post = await self.create_post(blog_id, 'blogger', 'new_post')
            await self.delete_post(blog_id, post['id'])
        except HttpError as error:
            raise Exception(f"Error: {error}") from error
        except Exception as e:
            return Exception(f"Error: {error}")

    async def create_post(self, blog_id, title, content, image=None, labels=list(), description="Test Description"):
        post = {
            'kind': 'blogger#post',
            'blog': {'id': blog_id},
            'title': title,
            'content': content,
            'labels': labels,
        }
        if description:
            post['metaDescription'] = description
        if image:
            post['images'] = [{'url': image}]
        return self.service.posts().insert(blogId=blog_id, body=post).execute()

    async def update_post(self, post_id, title=None, content=None, image=None):
        post = {'id': post_id}
        if title:
            post['title'] = title
        if content:
            post['content'] = content
        if image:
            post['images'] = [{'url': image}]
        return (
            self.service.posts()
            .patch(blogId=self.blogger_id, postId=post_id, body=post)
            .execute()
        )

    async def delete_post(self, blogger_id, post_id):
        self.service.posts().delete(blogId=blogger_id, postId=post_id).execute()

    async def list_posts(self, blog_id, max_results=10, order_by='PUBLISHED', page_token=None):
        result = self.service.posts().list(blogId=blog_id, maxResults=max_results,
                                           orderBy=order_by, pageToken=page_token).execute()
        return result.get('items', []), result.get('prevPageToken', None), result.get('nextPageToken', None)

    async def get_post(self, blog_id, post_id):
        return (
            self.service.posts()
            .get(blogId=blog_id, postId=post_id)
            .execute()
        )

    async def list_comments(self, post_id, max_results=10):
        result = self.service.comments().list(blogId=self.blogger_id, postId=post_id,
                                              maxResults=max_results).execute()
        return result.get('items', [])

    async def get_blogger_info(self, blogger_id):
        return self.service.blogs().get(blogId=blogger_id).execute()

    async def get_title(self, blog_id):
        result = self.service.blogs().get(blogId=blog_id).execute()
        return result.get('name')

    async def change_description(self, description):
        blog = self.service.blogs().get(blogId=self.blogger_id).execute()
        blog['description'] = description
        return self.service.blogs().patch(blogId=self.blogger_id, body=blog).execute()

    async def get_description(self, blog_id):
        result = self.service.blogs().get(blogId=blog_id).execute()
        return result.get('description')

    async def get_blog_address(self, blog_id):
        result = self.service.blogs().get(blogId=blog_id).execute()
        return result.get('url')

    async def get_blog_id(self, url):
        result = self.service.blogs().getByUrl(url=url).execute()
        return result['id']

    async def get_blog_labels(self, blog_id):
        blog_url = await self.get_blog_address(blog_id)
        res = requests.get(f"{blog_url}/feeds/posts/default?alt=json").json()
        labels = res["feed"].get("category") or []
        return [label['term'] for label in labels]


blogger = Blogger(Config.BLOG_ID)
