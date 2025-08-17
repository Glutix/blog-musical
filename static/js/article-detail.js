

document.addEventListener("DOMContentLoaded", function () {
    // Funcion para obtener el CSRF token de forma segura
    function getCsrfToken(form) {
        // Busca el token en el formulario actual
        if (form) {
            const tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
            if (tokenInput) {
                return tokenInput.value;
            }
        }
        // Fallback: busca en el DOM
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenInput) {
            return tokenInput.value;
        }
        const tokenCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        if (tokenCookie) {
            return tokenCookie.split('=')[1];
        }
        console.error('CSRF Token no encontrado.');
        return null;
    }

    const container = document.getElementById('article-detail-container');
    if (!container) return;

    // --- Modal de confirmación de borrado ---
    const deleteModalElement = document.getElementById('confirmDeleteModal');
    const confirmDeleteModal = deleteModalElement ? new bootstrap.Modal(deleteModalElement) : null;
    let commentUrlToDelete = null; // Guardaremos la URL para el borrado

    // =======================================================
    // ENVÍO DE NUEVO COMENTARIO Y RESPUESTA POR AJAX
    // =======================================================
    // Intercepta solo el formulario principal de comentarios por su id
    const mainCommentForm = document.getElementById('main-comment-form');
    if (mainCommentForm) {
        mainCommentForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const csrfToken = getCsrfToken(mainCommentForm);
            const textarea = mainCommentForm.querySelector('textarea[name="content"]');
            const parentIdInput = mainCommentForm.querySelector('input[name="parent_id"]');
            const content = textarea ? textarea.value.trim() : '';
            const parent_id = parentIdInput ? parentIdInput.value : '';
            if (!content) return;

            fetch(mainCommentForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ content, parent_id })
            })
                .then(async res => {
                    try {
                        const data = await res.json();
                        if (data && data.success && data.comment_html) {
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = data.comment_html;
                            const commentsContainer = document.getElementById('comments-container');
                            if (commentsContainer) {
                                const newCommentElem = tempDiv.firstElementChild;
                                commentsContainer.prepend(newCommentElem);
                                textarea.value = '';
                                // Espera a que el DOM lo inserte y luego hace scroll
                                // Fade-in visual
                                newCommentElem.classList.add('fade-in-comment');
                                setTimeout(() => {
                                    newCommentElem.classList.add('visible');
                                    // Busca el id del nuevo comentario
                                    const commentId = newCommentElem.id;
                                    const scrollTarget = document.getElementById(commentId);
                                    if (scrollTarget) {
                                        scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    }
                                }, 100);
                            }
                        } else if (data && data.error) {
                            alert(data.error);
                        }
                    } catch (err) {
                        // Si no es JSON, no mostrar alert (el comentario igual se publicó)
                    }
                })
        });
    }

    // Intercepta los formularios de respuesta (reply) usando delegación
    container.addEventListener('submit', function (e) {
        const form = e.target;
        if (form.classList.contains('reply-form-wrapper')) {
            e.preventDefault();
            const csrfToken = getCsrfToken(form);
            const textarea = form.querySelector('textarea[name="content"]');
            const parentIdInput = form.querySelector('input[name="parent_id"]');
            const content = textarea ? textarea.value.trim() : '';
            const parent_id = parentIdInput ? parentIdInput.value : '';
            if (!content) return;

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ content, parent_id })
            })
                .then(async res => {
                    try {
                        const data = await res.json();
                        if (data && data.success && data.comment_html) {
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = data.comment_html;
                            const repliesContainer = document.getElementById(`reply-form-${parent_id}`)?.parentNode?.querySelector('.replies-divider');
                            if (repliesContainer) {
                                const replyElem = tempDiv.firstElementChild;
                                replyElem.classList.add('fade-in-comment');
                                repliesContainer.appendChild(replyElem);
                                // Forzar reflow antes de agregar la clase visible
                                void replyElem.offsetWidth;
                                setTimeout(() => {
                                    replyElem.classList.add('visible');
                                    const replyId = replyElem.id;
                                    const scrollTarget = document.getElementById(replyId);
                                    if (scrollTarget) {
                                        scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                    }
                                }, 100);
                            } else {
                                window.location.reload();
                            }
                            // Oculta el formulario de respuesta
                            form.closest('.reply-form-container').classList.add('d-none');
                            textarea.value = '';
                        } else if (data && data.error) {
                            alert(data.error);
                        }
                    } catch (err) {
                        // Si no es JSON, no mostrar alert (la respuesta igual se publicó)
                    }
                })
        }
    });

    // =======================================================
    // DELEGACIÓN DE EVENTOS PRINCIPAL (likes, editar, eliminar, etc)
    // =======================================================
    container.addEventListener('click', function (e) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) return;

        // Buscamos el botón más cercano al clic para asegurar que capturamos el evento
        const button = e.target.closest('button');
        if (!button) return;

        // --- Manejador del botón "Me Gusta" del ARTÍCULO ---
        if (button.id === 'like-button') {
            e.preventDefault();
            handleArticleLike(button, csrfToken);
        }

        // --- Manejador del botón "Me Gusta" de un COMENTARIO ---
        else if (button.classList.contains('comment-like-btn')) {
            e.preventDefault();
            handleCommentLike(button, csrfToken);
        }

        // --- Manejador del botón "Responder" ---
        else if (button.classList.contains('reply-btn')) {
            e.preventDefault();
            toggleReplyForm(button.dataset.commentId);
        }

        // --- Manejador del botón "Cancelar respuesta" ---
        else if (button.classList.contains('cancel-reply')) {
            e.preventDefault();
            const formContainer = button.closest('.reply-form-container');
            if (formContainer) {
                formContainer.classList.add('d-none');
            }
        }

        // --- Manejador del botón "Editar comentario" ---
        else if (button.classList.contains('edit-btn')) {
            e.preventDefault();
            const commentId = button.dataset.id;
            const content = button.dataset.content;
            const commentWrapper = document.getElementById(`comment-${commentId}`);
            if (!commentWrapper) return;

            // Evita múltiples formularios de edición
            if (commentWrapper.querySelector('.edit-controls')) return;

            // Oculta el texto original
            const commentText = commentWrapper.querySelector('.comment-text');
            if (commentText) commentText.style.display = 'none';

            // Crea el formulario de edición inline
            const editForm = document.createElement('form');
            editForm.className = 'edit-controls mt-2';
            editForm.innerHTML = `
                <textarea class="form-control mb-2" rows="2" required style="border-radius:8px;">${content}</textarea>
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-orange btn-sm">Guardar</button>
                    <button type="button" class="btn btn-outline-secondary btn-sm cancel-edit">Cancelar</button>
                </div>
            `;

            // Inserta el formulario después del texto
            if (commentText) commentText.parentNode.insertBefore(editForm, commentText.nextSibling);

            // Cancelar edición
            editForm.querySelector('.cancel-edit').addEventListener('click', function (ev) {
                ev.preventDefault();
                editForm.remove();
                if (commentText) commentText.style.display = '';
            });

            // Guardar edición (AJAX)
            editForm.addEventListener('submit', function (ev) {
                ev.preventDefault();
                const newContent = editForm.querySelector('textarea').value.trim();
                if (!newContent) return;
                const url = button.dataset.url;
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ content: newContent })
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data && data.success) {
                            // Actualiza el texto del comentario
                            if (commentText) {
                                // Reemplaza todo el bloque .comment-text por el HTML renderizado
                                const tempDiv = document.createElement('div');
                                tempDiv.innerHTML = data.content_html || newContent;
                                commentText.replaceWith(tempDiv.firstElementChild);
                            }
                            editForm.remove();
                        } else {
                            alert(data && data.error ? data.error : 'Error al editar el comentario.');
                        }
                    })
                    .catch(() => alert('Error al editar el comentario.'));
            });
        }

        // --- Manejador del botón "Eliminar" (abre el modal) ---
        else if (button.classList.contains('delete-btn')) {
            e.preventDefault();
            commentUrlToDelete = button.dataset.url; // Guardamos la URL del atributo data-url del botón
            if (confirmDeleteModal) {
                confirmDeleteModal.show();
            }
        }
    });

    // --- Manejador del botón de confirmación de borrado en el MODAL ---
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (commentUrlToDelete) {
                handleCommentDelete(commentUrlToDelete, getCsrfToken());
            }
        });
    }

    // =======================================================
    // FUNCIONES LÓGICAS
    // =======================================================

    async function fetchData(url, csrfToken) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error en la petición fetch:', error);
            return null;
        }
    }

    function handleArticleLike(button, csrfToken) {
        button.disabled = true;
        const url = button.dataset.url; // Leemos la URL desde el HTML

        fetchData(url, csrfToken).then(data => {
            if (data) {
                const likeCountSpan = document.getElementById('like-count');
                const icon = button.querySelector('i');
                updateLikeUI(likeCountSpan, icon, data.total_likes, data.is_liked);
            }
        }).finally(() => {
            button.disabled = false;
        });
    }

    function handleCommentLike(button, csrfToken) {
        button.disabled = true;
        const url = button.dataset.url; // Leemos la URL desde el HTML

        fetchData(url, csrfToken).then(data => {
            if (data) {
                const likeCountSpan = button.querySelector('.comment-like-count');
                const icon = button.querySelector('i');
                updateLikeUI(likeCountSpan, icon, data.total_likes, data.is_liked);
            }
        }).finally(() => {
            button.disabled = false;
        });
    }

    function handleCommentDelete(url, csrfToken) {
        const confirmButton = document.getElementById('confirmDeleteBtn');
        confirmButton.disabled = true;

        fetchData(url, csrfToken).then(data => {
            if (data && data.success) {
                const commentId = url.match(/comentario\/(\d+)\/eliminar-ajax/)[1];
                const commentElement = document.getElementById(`comment-${commentId}`);
                if (commentElement) {
                    commentElement.style.transition = 'opacity 0.4s ease-out';
                    commentElement.style.opacity = '0';
                    setTimeout(() => commentElement.remove(), 400);
                }
            } else {
                console.error("Error al eliminar comentario:", data ? data.error : 'Respuesta nula');
            }
        }).finally(() => {
            if (confirmDeleteModal) confirmDeleteModal.hide();
            commentUrlToDelete = null;
            confirmButton.disabled = false;
        });
    }

    function toggleReplyForm(commentId) {
        const replyFormContainer = document.getElementById(`reply-form-${commentId}`);
        if (replyFormContainer) {
            const isHidden = replyFormContainer.classList.contains('d-none');
            // Oculta todos los otros formularios
            document.querySelectorAll('.reply-form-container').forEach(form => form.classList.add('d-none'));

            // Muestra solo el actual si estaba oculto
            if (isHidden) {
                replyFormContainer.classList.remove('d-none');
                const textarea = replyFormContainer.querySelector('textarea');
                if (textarea) textarea.focus();
            }
        }
    }
});

function updateLikeUI(likeCountSpan, icon, totalLikes, isLiked) {
    if (likeCountSpan) {
        likeCountSpan.textContent = totalLikes;
    }
    if (icon) {
        if (isLiked) {
            icon.classList.remove('far', 'fa-heart');
            icon.classList.add('fas', 'fa-heart', 'text-danger');
        } else {
            icon.classList.remove('fas', 'fa-heart', 'text-danger');
            icon.classList.add('far', 'fa-heart');
        }
    }
}


document.getElementById("shareBtn").addEventListener("click", function () {
    const currentUrl = window.location.href;
    navigator.clipboard.writeText(currentUrl)
        .then(() => {
            const toastEl = document.getElementById('shareToast');
            const toast = new bootstrap.Toast(toastEl, { delay: 2000 }); // 2 segundos
            toast.show();
        })
        .catch(err => {
            console.error("Error al copiar el enlace: ", err);
        });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".truncate-text").forEach(elem => {
        const maxLength = parseInt(elem.dataset.maxLength, 10);
        const fullText = elem.innerText.trim();

        if (fullText.length > maxLength) {
            const truncated = fullText.slice(0, maxLength) + "... ";
            elem.innerText = truncated;

            const toggleBtn = document.createElement("button");
            toggleBtn.innerText = "Ver más";
            toggleBtn.className = "btn btn-link p-0 text-orange fw-bold";
            toggleBtn.style.fontSize = "0.9rem";

            elem.appendChild(toggleBtn);

            let expanded = false;
            toggleBtn.addEventListener("click", () => {
                expanded = !expanded;
                elem.innerText = expanded ? fullText + " " : truncated;
                toggleBtn.innerText = expanded ? "Ver menos" : "Ver más";
                elem.appendChild(toggleBtn); // reinsertar el botón
            });
        }
    });
});