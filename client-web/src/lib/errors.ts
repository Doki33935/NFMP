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

const DETAIL_MESSAGES: Record<string, string> = {
  'Cannot complete': 'Карточку можно оформить только из статуса «На проверке»',
  'Coordinates must be provided together': 'Поставьте точку пожара на карте заново',
  'Coordinates must be within the Orenburg region': 'Точка пожара должна находиться в Оренбургской области',
  'Editing not allowed': 'Редактировать оформленную карточку может только администратор',
  'End time cannot precede the message time': 'Дата и время ликвидации не могут быть раньше времени сообщения',
  'External card number already exists': 'Такой номер карточки ААС КНД уже используется',
  'Fire date must match the message date': 'Дата пожара должна совпадать с датой сообщения',
  'Fire has already been taken': 'Карточку уже принял в работу другой дознаватель',
  'Fire not found': 'Карточка пожара не найдена',
  'Select a valid owner type': 'Выберите собственника из списка',
  'Select a valid ZOUIT type': 'Выберите тип ЗОУИТ из списка',
  'Take the fire before editing': 'Сначала примите карточку в работу',
  'The selected settlement does not belong to the municipality': 'Выбранный сельсовет не относится к указанному муниципальному образованию',
}

type ValidationIssue = {
  loc?: Array<string | number>
  msg?: string
}

function validationIssueMessage(issue: ValidationIssue): string {
  const field = [...(issue.loc || [])].reverse().find((part) => typeof part === 'string')
  const label = field ? FIELD_LABELS[field] || field : 'Поле'
  const message = (issue.msg || 'проверьте значение').replace(/^Value error,\s*/i, '')

  if (message === 'Field required') return `${label}: поле не заполнено`
  if (message === 'Address is required') return 'Адрес: поле не заполнено'
  if (message === 'Latitude and longitude must be provided together') return 'Поставьте точку пожара на карте заново'
  if (message === 'Latitude and longitude must be updated together') return 'Поставьте точку пожара на карте заново'
  if (message.includes('at least 1 character')) return `${label}: поле не заполнено`
  if (message.includes('greater than or equal to')) return `${label}: значение слишком мало`
  if (message.includes('valid number')) return `${label}: укажите число`
  return `${label}: ${DETAIL_MESSAGES[message] || message}`
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback

  const detail = error.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return DETAIL_MESSAGES[detail] || detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map(validationIssueMessage).join('; ')
  }

  if (!error.response) return 'Нет связи с сервером. Проверьте подключение и повторите попытку'
  if (error.response.status >= 500) return 'Сервер не смог сохранить данные. Повторите попытку или обратитесь к администратору'

  return fallback
}
