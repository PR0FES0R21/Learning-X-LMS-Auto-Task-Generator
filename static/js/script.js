$(document).ready(function () {
    if(window.location.pathname == '/daftar/tugas') {
        getTugas();
    }
    
    if( window.location.pathname == '/kerjakan/tugas') {
        getKuis()
    }

    if( window.location.pathname == '/confirmasi/tugas') {
        listingConfirmasiTugas()
    }
    
    if( window.location.pathname == '/detail/user' ) {
        const name = new URLSearchParams(window.location.search).get('name');
        listingConfirmasiTugas(name)
    }
    
    if( window.location.pathname == '/kelola/user' ) {
        showUserAdmin();
    }

    if( window.location.pathname == '/recovery/user' ) {
        getRecovery();
    }

    if( window.location.pathname  == '/tracking/actifitys') {
        getDataTrack()
    }

    alerts()

    const userAgent = navigator.userAgent;

})

function cekUsername() {
    const searchInput = $('#username');
    const searchResult = $('#searchResult');
    const button = $('#button')
  
    searchInput.on('input', function() {
        const query = searchInput.val();    
        $.ajax({
            url: `/check?q=${query}`,
            type: 'GET',
            success: function(data) {
                if (data.exists) {
                    if( session_username ) {
                        if(query == session_username) {
                            $('#icon').html('<i class="fa-regular fa-circle-check text-success fa-beat"></i>')
                            $('#button').prop('disabled', false)
                            searchResult.text('');
                        } else {
                            $('#icon').html('<i class="fa-regular fa-circle-xmark text-danger fa-beat"></i>')
                            $('#button').prop('disabled', true)
                            searchResult.text('Username Tidak Valid.');
                        }
                    } else {
                        $('#icon').html('<i class="fa-regular fa-circle-xmark text-danger fa-beat"></i>')
                            $('#button').prop('disabled', true)
                            searchResult.text('Username Tidak Valid.');
                    }
                } else {
                    if( query.length < 5 ) {
                        $('#icon').html('<i class="fa-regular fa-circle-xmark text-danger fa-beat"></i>')
                        $('#button').prop('disabled', true)
                        searchResult.text('Karakter Harus Lebih Dari 5 Huruf.');
                    } else {
                        $('#icon').html('<i class="fa-regular fa-circle-check text-success fa-beat"></i>')
                        $('#button').prop('disabled', false)
                        searchResult.text('Username Valid.');
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('Terjadi kesalahan dalam request:', status, error);
            }
        });
    });
}

// Panggil fungsi cekUsername
cekUsername();


function alerts(messages) {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('msg');
    if(message || messages) {
        $('#alert').html(`<div id="alert" class="alert alert-info rounded-0" role="alert">${message ? message : messages}</div>`)
        setTimeout(() => {
            $('#alert').hide()
            if( message ) {
                const url = new URL(window.location.href);
                url.search = '';
                window.history.replaceState({}, document.title, url.toString());
            }
        }, 2000);
    }
}

function getUser() {
    $.ajax({
        type: 'GET',
        url: '/getData?collection=users',
        data: {},
        success: response => {
            response = response.data
            response.forEach(user => {
                temp_html = `<option value="${user.username}">${user.username}</option>`;
                $('#select-user').append(temp_html);
            });
        }
    })
}

function getTugas() {
    $.ajax({
        type: 'GET',
        url: '/getData?collection=file_tugas',
        data: {},
        success: response => {
            response = response.data

            response.forEach(file => {
                temp_html = `
                <div class="container my-2">
                    <div class="row border d-flex align-items-center py-1 shadow mx-1">
                        <div class="col-2">
                            <img src="http://localhost:8080/static/image/logo-tugas.jpg" alt="Gambar Kecil" class="rounded-1" width="55">
                        </div>
                        <div class="col">
                            <span class="d-block">${file.tugasName}</span>
                            <span class="d-block" style="font-size: 0.6rem;">${file.keterangan}</span>
                        </div>
                        <div class="col text-end">
                            <form action="/download" method="post">
                                <input type="hidden" name="status" value="${file.keterangan === 'perlu upload github dan glitch' ? 'Hubungi!' : 'Kerjakan'}">
                                <button type="submit" value="${file.fileName}" name="tugas" class="btn download-tugas ${file.keterangan === 'perlu upload github dan glitch' ? 'btn-warning' : 'btn-success'}">${file.keterangan === 'perlu upload github dan glitch' ? 'Hubungi!' : 'Kerjakan'}</button>
                            </form>
                        </div>
                    </div>
                </div>
                `;
                $('#file-tugas').append(temp_html);
            });
        }
    });
}

function getKuis() {
    const urlParams = new URLSearchParams(window.location.search);
    const filename = urlParams.get('filename');

    $.ajax({
        type: 'GET',
        url: `/getKuis?nomorKuis=${filename}`,
        data: {},
        success: response => {
            response.data.forEach(item => {
                $('#container').append(
                    `<div class="kuis bg-primary bg-gradient rounded-1 py-2 mt-2">
                    <div class="mx-2">
                      <div class="soal">${item.soalKuis}</div>
                      <div class="jawaban">Jawaban: <span class="user-select-all">${item.jawabanKuis}</span></div>
                    </div>
                  </div>`
                )
            })
        }
    });
}



// // Menggunakan event delegation untuk menangani klik tombol-tombol yang ditambahkan secara dinamis
// $('#file-tugas').on('click', '.download-tugas', function() {
//     var fileName = $(this).val();
//     const selectedUser = 'nabil';
//     console.log(fileName, selectedUser)

//     $.ajax({
//         type: 'POST',
//         url: '/download',
//         data : {
//             'user': selectedUser,
//             'tugas': fileName
//         },   
//     });

// });

function deleteFolder(folderName) {
    let password = prompt('Masukan Password: ')
    if (password === 'profesor') {
        if (confirm("Are you sure you want to delete " + folderName + "?")) {
            
            $.ajax({
                type: 'POST',
                url: '/delete_folder',
                data: {
                    folderName: folderName
                },
                success: response => {
                    alert(response.msg)
                    location.reload();
                }
            })
        }
    } else {
        alert('Pasword salah!')
    }
}

function deleteFile(filename) {
    if (confirm("Are you sure you want to delete " + filename + "?")) {
        $.ajax({
            type: 'POST',
            url: '/delete_file',
            data: {
                filename: filename
            },
            success: response => {
                alert(response.msg)
                location.reload();
            }
        })
    }
}

function downloadFile(filename) {
    window.location.href = `/download_manual?filename=${filename}`
}

function prepareConfirm(minggu, user = 'false') {
    if(confirm(`Yakin Minggu${minggu} Sudah Selesai?`)) {
        $.ajax({
            type: 'POST',
            url: '/confirmasi/tugas',
            data: {
                minggu: minggu,
                user: user,
                user_agent: navigator.userAgent
            },
            success: response => {
                listingConfirmasiTugas(response.name)
            }
        })
    }
}
function listingConfirmasiTugas(user = false) {
    $.ajax({
        type: 'GET',
        url: `/get/confirmasi/tugas${!user?'':'?name='+user}`,
        data: {},
        success: response => {
            response.forEach(item => {
                $(`#minggu${item.minggu}`).text(session == 'Administrator' || session == 'Premium' ? item.date +" "+ item.time : item.date)
                $(`#status${item.minggu}`).html('<button class="btn btn-outline-success disabled" aria-disabled="true"><i class="fa-solid fa-circle-check"></i> Selesai</button>')
            })
        }
    });
}
function showUserAdmin() {
    $.ajax({
        type: 'GET',
        url: '/getData?collection=users',
        data: {},
        success: response => {
            response = response.data
            let i = 1;
            response.forEach(user => {
            let temp_html = `
            <tr class="text-center">
              <th scope="row">${i}</th>
              <td>${user.username}</td>
              <td>${user.selesai}</td>
              <td>
                <div style="font-size: 1.1rem;">
                    <i class="fa-solid fa-user-pen pointer bg-warning p-1 rounded-1" 
                        data-bs-toggle="modal" 
                        data-bs-target="#modalupdateuser" onclick="updateUser('${user.username}')">
                    </i> | 
                    <i class="fa-solid fa-circle-info pointer text-info bg-info p-1 rounded-1 bg-opacity-25" onclick="window.location.href = '/detail/user?name=${user.username}'"></i>
                    </i> | 
                    <i class="fa-solid fa-trash pointer text-danger bg-danger bg-opacity-25 p-1 rounded-1" onclick="deleteUser('${user.username}')"></i>
                </div>                           
              </td>
            </tr>`
            $('#user').append(temp_html)
            i++
            });
        }
    })
}

function getSession(session_name) {
    $.ajax({
        type: 'GET',
        url: '/getSession',
        data: {
            name: session_name
        },
        success: response => {
            return response
        }
    })
}

function updateUser(username) {
    $.ajax({
        type: 'GET',
        url: '/update/user',
        data: {
            username: username
        },
        success: response => {
            $('#name').val(response.name)
            $('#username').val(response.username)
            $('#password').val(response.password)
            $('#mongodb-url').val(response.mongodbUrl)
            $('#db-name').val(response.dbname)
            $('#email').val(response.email)
            $('#select-user').val(response.level)
        }

    })
}

function deleteUser(username) {
    $.ajax({
        type: 'POST',
        url: '/delete/user',
        data: {
            username: username,
        },
        success: response =>  {
            window.location.href = `/kelola/user?msg=${response.msg}`
        }
    })
}

function livesearch() {
    const searchInput = document.getElementById('searchInput');
        const dataTable = document.getElementById('dataTable');

        searchInput.addEventListener('input', function() {
            const searchText = this.value.toLowerCase();
            const rows = dataTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

            for (let i = 0; i < rows.length; i++) {
                const cells = rows[i].getElementsByTagName('td');
                let found = false;
                for (let j = 0; j < cells.length; j++) {
                    const cellText = cells[j].textContent.toLowerCase();
                    if (cellText.includes(searchText)) {
                        found = true;
                        break;
                    }
                }
                if (found) {
                    rows[i].style.display = '';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        });
}

function getRecovery() {
    $.ajax({
        type: 'GET',
        url: '/get/recovery',
        data: {},
        success: response => {
            if( response.length > 0 ) {
                let i = 1
                response.forEach(items => {
                    let temp_html = `
                    <tr>
                        <th scope="row">${i}</th>
                        <td>${items.username}</td>
                        <td><button class="btn btn-danger btn-sm" onclick="deletePermanent('${items.username}')"><i class="fa-solid fa-user-xmark"></i> Permanent</button></td>
                        <td><button class="btn btn-secondary btn-sm" onclick="recovery('${items.username}')"><i class="fa-solid fa-hammer"></i> Pulihkan</button></td>
                    </tr>`
                    $('#table').append(temp_html)
                    i++
                })
            } else {
                let temp_html = `
                <div class="text-center">
                    <p>Tidak Ada Data Apapun</p>
                </div>`
                $('#info').append(temp_html)
            }
        }
    })
}

function recovery(username) {
    $.ajax({
        type: 'POST',
        url: '/recovery/user',
        data: {
            username: username
        },
        success: response => {
            window.location.href = `/recovery/user?msg=${response.msg}`
        }
    })
}

function deletePermanent(username) {
    if( confirm('Data Akan Dihapus Secara Permanent!')) {
        if(prompt('masukan password: ') == 'profesor') {
            $.ajax({
                type: 'POST',
                url: '/delete/data',
                data: {
                    collection: 'users_deleted',
                    key: 'username',
                    value: username
                },
                success: response => {
                    window.location.href = '/recovery/user?msg="Data Dihapus Secara Permanent"'
                }
            })
        }
        else {
            alert('password salah')
        }
    }
}

function getDataTrack() {
    $.ajax({
        type: 'GET',
        url: '/getData',
        data: {
            collection: 'tracking'
        },
        success: response => {
            response.data.forEach(data => {
                let temp_html = `
                <div class="text-start mx-2 py-3 border-bottom border-black">
                    <div class="user"><i class="fa-solid fa-user-secret fa-2x"></i> ID: ${data.id},<span class="ms-2 bg-danger p-1 rounded-1 text-warning">IP Address: ${data.ip}</span></div>
                    <div class="aktifitas text-primary">${data.user_agent}</div>
                    <div class="aktifitas"><i class="fa-solid fa-mobile-screen-button text-success"></i> ${data.device, data.browser, data.version}</div>
                    <div class="waktu" style="font-size: 0.7rem;">${data.waktu}<span class="ms-2">${data.actifity}</span></div>
                </div>`
                $('#tracking').append(temp_html)
            })
        }
    })
}

// function downloadTugas() {
//     $('.download-tugas').click(function() {
//         const selectedUser = $('#select-user').val();
//         const tugasName = $(this).val(); // Nilai dari tombol yang diklik

//         // Kirim data menggunakan AJAX
//         $.ajax({
//             type: 'POST',
//             url: '/test',
//             contentType: 'application/json',
//             data: JSON.stringify({
//                 user: selectedUser,
//                 tugas: tugasName
//             }),
//             success: function(response) {
//                 console.log('Berhasil mendownload', response.msg);
//             },
//             error: function() {
//                 console.error('Terjadi kesalahan saat mendownload');
//             }
//         });
//     });
// }