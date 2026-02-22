import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Spinner, Badge, FormSelect, Row, Col } from 'react-bootstrap'
import { getAssets, createAsset, deleteAsset, Asset, AssetCreate } from '../api/assets'

const Assets = () => {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const limit = 10

  const [newAsset, setNewAsset] = useState<AssetCreate>({
    name: '',
    type: 'computer',
    status: 'available',
  })

  useEffect(() => {
    fetchAssets()
  }, [page, statusFilter, typeFilter])

  const fetchAssets = async () => {
    setLoading(true)
    try {
      const data = await getAssets({
        skip: page * limit,
        limit,
        status: statusFilter || undefined,
        type: typeFilter || undefined,
      })
      setAssets(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('Failed to fetch assets:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await createAsset(newAsset)
      setShowModal(false)
      fetchAssets()
      setNewAsset({ name: '', type: 'computer', status: 'available' })
    } catch (error) {
      console.error('Failed to create asset:', error)
    }
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Удалить оборудование?')) {
      try {
        await deleteAsset(id)
        fetchAssets()
      } catch (error) {
        console.error('Failed to delete asset:', error)
      }
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      available: 'success',
      in_use: 'primary',
      maintenance: 'warning',
      disposed: 'danger',
    }
    const labels: Record<string, string> = {
      available: 'Доступно',
      in_use: 'Используется',
      maintenance: 'На обслуживании',
      disposed: 'Списано',
    }
    return <Badge bg={colors[status] || 'secondary'}>{labels[status] || status}</Badge>
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      computer: 'Компьютер',
      laptop: 'Ноутбук',
      monitor: 'Монитор',
      phone: 'Телефон',
      printer: 'Принтер',
      furniture: 'Мебель',
      other: 'Другое',
    }
    return labels[type] || type
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <div className="page-header d-flex justify-content-between align-items-center">
        <h1>Оборудование</h1>
        <Button onClick={() => setShowModal(true)}>
          + Добавить оборудование
        </Button>
      </div>

      <Row className="mb-3">
        <Col md={3}>
          <FormSelect
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="">Все типы</option>
            <option value="computer">Компьютер</option>
            <option value="laptop">Ноутбук</option>
            <option value="monitor">Монитор</option>
            <option value="phone">Телефон</option>
            <option value="printer">Принтер</option>
            <option value="furniture">Мебель</option>
            <option value="other">Другое</option>
          </FormSelect>
        </Col>
        <Col md={3}>
          <FormSelect
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Все статусы</option>
            <option value="available">Доступно</option>
            <option value="in_use">Используется</option>
            <option value="maintenance">На обслуживании</option>
            <option value="disposed">Списано</option>
          </FormSelect>
        </Col>
      </Row>

      {loading ? (
        <div className="loading-spinner">
          <Spinner animation="border" />
        </div>
      ) : (
        <>
          <Table hover responsive>
            <thead>
              <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Тип</th>
                <th>Серийный номер</th>
                <th>Статус</th>
                <th>Дата покупки</th>
                <th>Цена</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.asset_id}>
                  <td>{asset.asset_id}</td>
                  <td>{asset.name}</td>
                  <td>{getTypeLabel(asset.type)}</td>
                  <td>{asset.serial_number || '-'}</td>
                  <td>{getStatusBadge(asset.status)}</td>
                  <td>{asset.purchase_date || '-'}</td>
                  <td>{asset.purchase_price ? `${asset.purchase_price} ₽` : '-'}</td>
                  <td>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleDelete(asset.asset_id)}
                    >
                      Удалить
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="d-flex justify-content-between align-items-center">
            <span>Всего: {total}</span>
            <div className="d-flex gap-2">
              <Button
                variant="outline-primary"
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
              >
                Назад
              </Button>
              <span className="py-2">{page + 1} / {totalPages || 1}</span>
              <Button
                variant="outline-primary"
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
              >
                Вперёд
              </Button>
            </div>
          </div>
        </>
      )}

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Новое оборудование</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Название</Form.Label>
              <Form.Control
                value={newAsset.name}
                onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Тип</Form.Label>
              <Form.Select
                value={newAsset.type}
                onChange={(e) => setNewAsset({ ...newAsset, type: e.target.value })}
              >
                <option value="computer">Компьютер</option>
                <option value="laptop">Ноутбук</option>
                <option value="monitor">Монитор</option>
                <option value="phone">Телефон</option>
                <option value="printer">Принтер</option>
                <option value="furniture">Мебель</option>
                <option value="other">Другое</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Серийный номер</Form.Label>
              <Form.Control
                value={newAsset.serial_number || ''}
                onChange={(e) => setNewAsset({ ...newAsset, serial_number: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Дата покупки</Form.Label>
              <Form.Control
                type="date"
                value={newAsset.purchase_date || ''}
                onChange={(e) => setNewAsset({ ...newAsset, purchase_date: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Цена</Form.Label>
              <Form.Control
                type="number"
                value={newAsset.purchase_price || ''}
                onChange={(e) => setNewAsset({ ...newAsset, purchase_price: Number(e.target.value) })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Статус</Form.Label>
              <Form.Select
                value={newAsset.status}
                onChange={(e) => setNewAsset({ ...newAsset, status: e.target.value })}
              >
                <option value="available">Доступно</option>
                <option value="in_use">Используется</option>
                <option value="maintenance">На обслуживании</option>
              </Form.Select>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Отмена
          </Button>
          <Button variant="primary" onClick={handleCreate}>
            Создать
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  )
}

export default Assets
