import axios from 'axios'

const FIELD_LABELS: Record<string, string> = {
  address: 'Адрес',
  area: 'Площадь',
  arrival_time: 'Время прибытия',
  end_time: 'Дата ликвидации',
  external_card_number: 'Номер карточки ААС КНД',
  fire_date: 'Дата пожара',
  full_name: 'ФИО',
  owner: 'Собственник',
  password: 'Пароль',
  password_confirmation: 'Подтверждение пароля',
  participant_id: 'Участник тушения',
  quantity: 'Количество техники',
  right_of_way_type: 'Тип ЗОУИТ',
  tech_type_id: 'Тип техники',
  time_msg: 'Время сообщения',
  username: 'Логин',
}

type ValidationIssue = {
  loc?: Array<string | number>
  msg?: string
}

function validationIssueMessage(issue: ValidationIssue): string {
  const field = [...(issue.loc || [])].reverse().find((part) => typeof part === 'string')
  const label = field ? FIELD_LABELS[field] || field : 'Поле'
  const message = issue.msg || 'проверьте значение'

  if (message === 'Field required') return `${label}: поле не заполнено`
  if (message.includes('at least 1 character')) return `${label}: поле не заполнено`
  if (message.includes('greater than or equal to')) return `${label}: значение слишком мало`
  if (message.includes('valid number')) return `${label}: укажите число`
  return `${label}: ${message}`
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback

  const detail = error.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map(validationIssueMessage).join('; ')
  }

  return fallback
}
