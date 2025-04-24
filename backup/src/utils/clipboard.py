import streamlit as st
import html
import pyperclip
import logging

logger = logging.getLogger(__name__)

def copy_to_clipboard(text: str) -> bool:
    """Копирует текст в буфер обмена."""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        logger.error(f"Ошибка при копировании в буфер обмена: {str(e)}")
        return False

def copy_to_clipboard_js(text: str):
    """Копирует текст в буфер обмена с использованием JavaScript."""
    # Экранируем специальные символы для JavaScript
    escaped_text = html.escape(text)
    
    js_code = f"""
    <script>
        async function copyText() {{
            try {{
                const text = "{escaped_text}";
                
                // Метод 1: navigator.clipboard API (предпочтительный метод)
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    try {{
                        await navigator.clipboard.writeText(text);
                        showNotification('Текст скопирован в буфер обмена', false);
                        return;
                    }} catch (err) {{
                        console.warn('Clipboard API failed:', err);
                    }}
                }}
                
                // Метод 2: document.execCommand (запасной метод)
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);
                
                if (successful) {{
                    showNotification('Текст скопирован в буфер обмена', false);
                    return;
                }}
                
                throw new Error('Не удалось скопировать текст');
            }} catch (err) {{
                console.error('Copy failed:', err);
                showNotification('Ошибка при копировании текста', true);
            }}
        }}
        
        function showNotification(message, isError) {{
            const notification = document.createElement('div');
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.backgroundColor = isError ? '#ff4444' : '#4CAF50';
            notification.style.color = 'white';
            notification.style.padding = '12px 24px';
            notification.style.borderRadius = '4px';
            notification.style.zIndex = '9999';
            notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            notification.style.transition = 'opacity 0.3s ease-in-out';
            notification.style.opacity = '1';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.style.opacity = '0';
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        document.body.removeChild(notification);
                    }}
                }}, 300);
            }}, 2000);
        }}
        
        copyText();
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True) 