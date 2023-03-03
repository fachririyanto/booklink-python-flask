function PopupShow(e) {
    e.preventDefault();

    const popupID = this.getAttribute('data-popup');
    console.log(popupID);

    document.getElementById(popupID).classList.remove('hidden');
    document.getElementById(popupID).classList.add('block');
}

function PopupClose(e) {
    e.preventDefault();

    const popupID = this.getAttribute('data-popup');

    document.getElementById(popupID).classList.add('hidden');
    document.getElementById(popupID).classList.remove('block');
}

function ShowEditFormPopup() {
    const linkID        = parseInt(this.getAttribute('data-id'));
    const $Link         = document.getElementById('link-' + linkID);
    const description   = $Link.querySelector('.link-title').textContent;
    const websiteUrl    = $Link.querySelector('.link-url').textContent;

    document.getElementById('link-website-url-edit').value = websiteUrl;
    document.getElementById('link-description-edit').value = description;
    document.getElementById('link-id-edit').value = linkID;
}

function RenderLinkItem(link_id, title, url) {
    return (
        `<article class="link-item w-1/4 px-3 pb-6" id="link-${link_id}">\
            <div class="relative h-full bg-gray-100 p-10 rounded-md">\
                <p class="link-url underline break-all">${url}</p>\
                <h3 class="link-title mt-6 text-lg font-medium leading-6">${title}</h3>\
                <div class="invisible mt-6">\
                    <p>\
                        <a href="#">\
                            <span class="material-symbols-outlined">edit</span>\
                        </a>\
                        <a href="#" class="ml-3">\
                            <span class="material-symbols-outlined">delete</span>\
                        </a>\
                    </p>\
                </div>\
                <div class="absolute bottom-10 left-10 right-10">\
                    <p class="flex relative z-10 items-center">\
                        <a href="#" class="link--button-edit btn--show-popup" data-id="${link_id}" data-popup="popup--edit-link">\
                            <span class="material-symbols-outlined">edit</span>\
                        </a>\
                        <a href="#" class="link--button-delete ml-3" data-id="${link_id}">\
                            <span class="material-symbols-outlined">delete</span>\
                        </a>\
                    </p>\
                </div>\
                <a target="_blank" href="${url}" class="absolute inset-0"></a>\
            </div>\
        </article>`
    );
}

function SaveLink(e) {
    e.preventDefault();

    const websiteUrl    = document.getElementById('link-website-url').value;
    const description   = document.getElementById('link-description').value;

    if (websiteUrl === '') {
        alert('Website URL required.');
        return;
    }

    let $Button = document.getElementById('button--add-link');

    $Button.setAttribute('disabled', 'disabled');
    $Button.querySelector('.loader').classList.remove('hidden');
    $Button.querySelector('.loader').classList.add('block');

    fetch('/api/link', {
        method  : 'POST',
        mode    : 'cors',
        headers : {
            'Content-Type': 'application/json',
        },
        body    : JSON.stringify({
            url     : websiteUrl,
            desc    : description,
        }),
    }).then(res => res.json()).then(res => {
        $Button.removeAttribute('disabled');
        $Button.querySelector('.loader').classList.add('hidden');
        $Button.querySelector('.loader').classList.remove('block');

        document.getElementById('form-add-link').reset();

        if (res.code === 200) {
            alert(res.message);

            document.getElementById('list-link').insertAdjacentHTML('afterbegin', RenderLinkItem(res.data.link_id, description, websiteUrl));

            document.getElementById(`link-${res.data.link_id}`).querySelector('.btn--show-popup').addEventListener('click', PopupShow);
            document.getElementById(`link-${res.data.link_id}`).querySelector('.link--button-edit').addEventListener('click', ShowEditFormPopup);
            document.getElementById(`link-${res.data.link_id}`).querySelector('.link--button-delete').addEventListener('click', DeleteLink);
        } else {
            alert(res.message);
        }
    });
}

function UpdateLink(e) {
    e.preventDefault();

    const websiteUrl    = document.getElementById('link-website-url-edit').value;
    const description   = document.getElementById('link-description-edit').value;
    const linkID        = document.getElementById('link-id-edit').value;

    if (websiteUrl === '') {
        alert('Website URL required.');
        return;
    }

    let $Button = document.getElementById('button--edit-link');

    $Button.setAttribute('disabled', 'disabled');
    $Button.querySelector('.loader').classList.remove('hidden');
    $Button.querySelector('.loader').classList.add('block');

    fetch('/api/link', {
        method  : 'PUT',
        mode    : 'cors',
        headers : {
            'Content-Type': 'application/json',
        },
        body    : JSON.stringify({
            link_id : linkID,
            url     : websiteUrl,
            desc    : description,
        }),
    }).then(res => res.json()).then(res => {
        $Button.removeAttribute('disabled');
        $Button.querySelector('.loader').classList.add('hidden');
        $Button.querySelector('.loader').classList.remove('block');

        if (res.code === 200) {
            alert(res.message);

            const $Link = document.getElementById(`link-${linkID}`);

            $Link.querySelector('.link-title').textContent = description;
            $Link.querySelector('.link-url').textContent = websiteUrl;
        } else {
            alert(res.message);
        }
    });
}

function DeleteLink(e) {
    e.preventDefault();

    const isConfirmed   = confirm('Are you sure?');
    const linkID        = parseInt(this.getAttribute('data-id'));

    if (isConfirmed) {
        fetch('/api/link', {
            method  : 'DELETE',
            mode    : 'cors',
            headers : {
                'Content-Type': 'application/json',
            },
            body    : JSON.stringify({
                link_id : linkID,
            }),
        }).then(res => res.json()).then(res => {
            if (res.code === 200) {
                document.getElementById(`link-${linkID}`).querySelector('.btn--show-popup').removeEventListener('click', PopupShow);
                document.getElementById(`link-${linkID}`).querySelector('.link--button-edit').removeEventListener('click', ShowEditFormPopup);
                document.getElementById(`link-${linkID}`).querySelector('.link--button-delete').removeEventListener('click', DeleteLink);

                document.getElementById(`link-${linkID}`).remove();
            } else {
                alert(res.message);
            }
        });
    }
}

function LoadMoreData(e) {
    e.preventDefault();

    const $Button = this;

    $Button.setAttribute('disabled', 'disabled');
    $Button.querySelector('.loader').classList.remove('hidden');
    $Button.querySelector('.loader').classList.add('block');

    let currentPage = parseInt($Button.getAttribute('data-page'));

    const params = new URLSearchParams({
        keyword : document.getElementById('form-keyword').value,
        limit   : 8,
        page    : currentPage + 1,
    });

    fetch('/api/link?' + params.toString()).then(res => res.json()).then(res => {
        if (res.code === 200) {
            let data = [], element = '';

            for ( var i in res.data ) {
                data = res.data[i];
                element += RenderLinkItem(data[0], data[1], data[2]);
            }

            const $ListLink = document.getElementById('list-link');
            const totalLink = parseInt($ListLink.getAttribute('data-total'));

            $ListLink.insertAdjacentHTML('beforeend', element);

            $Button.removeAttribute('disabled');
            $Button.querySelector('.loader').classList.add('hidden');
            $Button.querySelector('.loader').classList.remove('block');

            if (totalLink >= document.querySelectorAll('.link-item').length) {
                $Button.remove();
            }
        }
    }).catch(err => {
        console.log('load_more_action', err);
        alert('Failed to load data.');
    });
}

window.onload = () => {
    document.querySelectorAll('.btn--show-popup').forEach((elm) => {
        elm.addEventListener('click', PopupShow);
    });

    document.querySelectorAll('.btn--close-popup').forEach((elm) => {
        elm.addEventListener('click', PopupClose);
    });

    document.querySelectorAll('.link--button-edit').forEach((elm) => {
        elm.addEventListener('click', ShowEditFormPopup);
    });

    document.getElementById('form-add-link').addEventListener('submit', SaveLink);
    document.getElementById('form-edit-link').addEventListener('submit', UpdateLink);

    $ButtonLoadMore = document.getElementById('btn--load-more');
    if ($ButtonLoadMore) {
        $ButtonLoadMore.addEventListener('click', LoadMoreData);
    }

    document.querySelectorAll('.link--button-delete').forEach((elm) => {
        elm.addEventListener('click', DeleteLink);
    });
};