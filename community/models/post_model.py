# models/post_model.py

posts_db = [
    {
        "postId": 1,
        "title": "제목 1",
        "author": "더미 작성자1",
        "content": "이것은 1번 게시글의 아주 긴 상세 내용입니다. 목록에서는 보이지 않아야 합니다.",
        "profileImage": "https://image.kr/img.jpg",
        "createdAt": "2021-01-01 00:00:00",
        "likeCount": 0,
        "commentCount": 0,
        "viewCount": 0
    },
    {
        "postId": 2,
        "title": "제목 2",
        "author": "더미 작성자2",
        "content": "2번 게시글의 내용입니다. 역시 목록 조회 시에는 제외됩니다.",
        "profileImage": "https://image.kr/img.jpg",
        "createdAt": "2021-01-01 00:00:00",
        "likeCount": 5,
        "commentCount": 2,
        "viewCount": 10
    }
]

class PostModel:
    @staticmethod
    def get_all_posts():
        return posts_db