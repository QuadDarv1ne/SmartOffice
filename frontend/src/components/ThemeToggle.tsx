import { useEffect } from 'react'
import { Dropdown } from 'react-bootstrap'
import { useThemeStore } from '../store/themeStore'

export const ThemeToggle = () => {
  const { theme, setTheme, toggleTheme } = useThemeStore()

  return (
    <Dropdown>
      <Dropdown.Toggle variant="light" id="theme-toggle">
        {theme === 'light' ? '🌙' : '☀️'}
      </Dropdown.Toggle>

      <Dropdown.Menu align="end">
        <Dropdown.Item
          onClick={() => setTheme('light')}
          active={theme === 'light'}
        >
          ☀️ Светлая тема
        </Dropdown.Item>
        <Dropdown.Item
          onClick={() => setTheme('dark')}
          active={theme === 'dark'}
        >
          🌙 Тёмная тема
        </Dropdown.Item>
        <Dropdown.Divider />
        <Dropdown.Item onClick={toggleTheme}>
          🔄 Переключить
        </Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  )
}
