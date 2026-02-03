# models/comment_model.py
from datetime import datetime
from sqlalchemy import text
from database import engine

class CommentModel:
    
    @staticmethod
    def create_comment(comment_data: dict):
        """[DB 방식] 새 댓글을 생성하고 저장합니다."""
        with engine.connect() as conn:
            # SQL에서는 id를 자동 생성(Auto Increment)하므로 명시하지 않습니다.
            query = text("""
                INSERT INTO comments (post_id, user_id, content, created_at, updated_at)
                VALUES (:post_id, :user_id, :content, NOW(), NOW())
            """)
            result = conn.execute(query, {
                "post_id": comment_data["postId"],
                "user_id": comment_data["userId"], # controller에서 userId를 넘겨줘야 함
                "content": comment_data["content"]
            })
            conn.commit()
            return result.lastrowid # 생성된 댓글의 ID 반환

    @staticmethod
    def update_comment(comment_id: int, content: str):
        """댓글 내용을 수정합니다."""
        with engine.connect() as conn:
            query = text("""
                UPDATE comments 
                SET content = :content, updated_at = NOW()
                WHERE id = :comment_id AND deleted_at IS NULL
            """)
            result = conn.execute(query, {
                "content": content,
                "comment_id": comment_id
            })
            conn.commit()
            return result.rowcount > 0

    @staticmethod
    def get_comments_by_post_id(post_id: int):
        '''특정 게시글의 댓글 목록 조회'''
        with engine.connect() as conn:
            # 성능 향상을 위해 유저 테이블과 JOIN하여 닉네임과 프로필을 한 번에 가져옵니다.
            query = text("""
                SELECT c.id as commentId, c.content, c.created_at as createdAt,
                       u.id as userId, u.nickname as author, u.profile_url as profileImage
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.post_id = :post_id AND c.deleted_at IS NULL
                ORDER BY c.created_at ASC
            """)
            result = conn.execute(query, {"post_id": post_id}).fetchall()
            return [dict(row._mapping) for row in result]
        
    @staticmethod
    def get_comment_by_id(comment_id: int):
        '''특정 댓글 조회'''
        with engine.connect() as conn:
            query = text("""
                SELECT id as commentId, post_id as postId, user_id as userId, content
                FROM comments 
                WHERE id = :comment_id AND deleted_at IS NULL
            """)
            result = conn.execute(query, {"comment_id": comment_id}).fetchone()
            return dict(result._mapping) if result else None

    @staticmethod
    def delete_comment(comment_id: int):
        '''특정 댓글 삭제'''
        with engine.connect() as conn:
            query = text("""
                UPDATE comments 
                SET deleted_at = NOW() 
                WHERE id = :comment_id
            """)
            result = conn.execute(query, {"comment_id": comment_id})
            conn.commit()
            return result.rowcount > 0
    
    @staticmethod
    def delete_comments_by_post_id(post_id: int):
        '''특정 게시글에 달린 모든 댓글 삭제'''
        with engine.connect() as conn:
            # 해당 post_id를 가진 모든 댓글의 deleted_at 컬럼을 현재 시간으로 업데이트
            query = text("""
                UPDATE comments 
                SET deleted_at = NOW() 
                WHERE post_id = :post_id AND deleted_at IS NULL
            """)
            
            result = conn.execute(query, {"post_id": post_id})
            conn.commit()
            
            # 영향을 받은 행의 수(삭제된 댓글 수)를 반환하거나, 성공 여부를 반환
            return result.rowcount >= 0