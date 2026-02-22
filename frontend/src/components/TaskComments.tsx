import { useState, useEffect } from 'react'
import { Card, Form, Button, ListGroup, Badge } from 'react-bootstrap'
import { toast } from 'react-toastify'
import api from '../api/client'
import { useAuthStore } from '../store/authStore'

interface Comment {
  id: number
  task_id: number
  author_id: number
  author_email?: string
  author_name?: string
  content: string
  parent_id?: number
  is_edited: boolean
  is_deleted: boolean
  created_at: string
  updated_at: string
  replies_count?: number
}

interface TaskCommentsProps {
  taskId: number
}

export const TaskComments = ({ taskId }: TaskCommentsProps) => {
  const { user } = useAuthStore()
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [replyTo, setReplyTo] = useState<number | null>(null)

  const fetchComments = async () => {
    setLoading(true)
    try {
      const response = await api.get(`/api/tasks/${taskId}/comments`)
      setComments(response.data.comments || [])
    } catch (error: any) {
      toast.error('Ошибка загрузки комментариев')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComments()
  }, [taskId])

  const handleAddComment = async () => {
    if (!newComment.trim()) return

    setSubmitting(true)
    try {
      await api.post(`/api/tasks/${taskId}/comments`, {
        content: newComment,
        parent_id: replyTo,
      })
      
      setNewComment('')
      setReplyTo(null)
      toast.success('Комментарий добавлен')
      fetchComments()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка добавления комментария')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    if (!window.confirm('Удалить комментарий?')) return

    try {
      await api.delete(`/api/tasks/${taskId}/comments/${commentId}`)
      toast.success('Комментарий удалён')
      fetchComments()
    } catch (error: any) {
      toast.error('Ошибка удаления комментария')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const groupedComments = comments.reduce((acc, comment) => {
    if (comment.parent_id) {
      const parent = acc.find(c => c.id === comment.parent_id)
      if (parent) {
        if (!parent.replies) parent.replies = []
        parent.replies.push(comment)
      }
    } else {
      acc.push({ ...comment, replies: [] })
    }
    return acc
  }, [] as (Comment & { replies?: Comment[] })[])

  return (
    <Card>
      <Card.Header>
        <h5 className="mb-0">💬 Комментарии</h5>
      </Card.Header>
      <Card.Body>
        {/* Форма добавления */}
        <Form.Group className="mb-4">
          <Form.Label>
            {replyTo ? `Ответ на комментарий #${replyTo}` : 'Добавить комментарий'}
          </Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Напишите комментарий..."
          />
          <div className="d-flex gap-2 mt-2">
            <Button
              variant="primary"
              onClick={handleAddComment}
              disabled={!newComment.trim() || submitting}
            >
              {submitting ? 'Отправка...' : (replyTo ? 'Ответить' : 'Отправить')}
            </Button>
            {replyTo && (
              <Button variant="secondary" onClick={() => setReplyTo(null)}>
                Отмена
              </Button>
            )}
          </div>
        </Form.Group>

        {/* Список комментариев */}
        {loading ? (
          <div className="text-center text-muted">Загрузка...</div>
        ) : comments.length === 0 ? (
          <div className="text-center text-muted py-4">
            Нет комментариев. Будьте первым!
          </div>
        ) : (
          <ListGroup variant="flush">
            {groupedComments.map((comment) => (
              <div key={comment.id}>
                <ListGroup.Item className="border-0 px-0">
                  <div className="d-flex gap-3">
                    <div
                      className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center"
                      style={{ width: '40px', height: '40px', flexShrink: 0 }}
                    >
                      {(comment.author_email || '?')[0].toUpperCase()}
                    </div>
                    <div className="flex-grow-1">
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <strong>{comment.author_email || 'Пользователь'}</strong>
                          <small className="text-muted ms-2">
                            {formatDate(comment.created_at)}
                          </small>
                          {comment.is_edited && (
                            <Badge bg="secondary" className="ms-2">
                              изменено
                            </Badge>
                          )}
                        </div>
                        {comment.author_id === user?.id && (
                          <Button
                            variant="link"
                            size="sm"
                            className="text-danger p-0"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            🗑
                          </Button>
                        )}
                      </div>
                      <p className={`mt-2 mb-2 ${comment.is_deleted ? 'text-muted fst-italic' : ''}`}>
                        {comment.content}
                      </p>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0"
                        onClick={() => setReplyTo(comment.id)}
                      >
                        💬 Ответить
                      </Button>

                      {/* Ответы */}
                      {comment.replies && comment.replies.length > 0 && (
                        <div className="mt-2 ms-4 ps-3 border-start">
                          {comment.replies.map((reply) => (
                            <div key={reply.id} className="mb-2">
                              <div className="d-flex gap-2">
                                <div
                                  className="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center"
                                  style={{ width: '30px', height: '30px', flexShrink: 0 }}
                                >
                                  {(reply.author_email || '?')[0].toUpperCase()}
                                </div>
                                <div>
                                  <strong>{reply.author_email || 'Пользователь'}</strong>
                                  <small className="text-muted ms-2">
                                    {formatDate(reply.created_at)}
                                  </small>
                                  <p className="mt-1 mb-0">{reply.content}</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </ListGroup.Item>
                <hr className="my-2" />
              </div>
            ))}
          </ListGroup>
        )}
      </Card.Body>
    </Card>
  )
}
