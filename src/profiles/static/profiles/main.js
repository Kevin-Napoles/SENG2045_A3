const avatarBox = document.getElementById('avatar-box')
const avatarImage = avatarBox.querySelector('img')
const profileForm = document.getElementById('profile-form')
const csrf = profileForm.elements.csrfmiddlewaretoken
const bioInput = document.getElementById('id_bio')
const avatarInput = document.getElementById('id_avatar')
const alertBox = document.getElementById('alert-box')
const saveBtn = profileForm.querySelector('button[type="submit"]')

profileForm.addEventListener('submit', e => {
    e.preventDefault()
    if (saveBtn.disabled) return

    const submittedBio = bioInput.value
    const submittedAvatar = avatarInput.files[0]
    const formData = new FormData()
    formData.append('csrfmiddlewaretoken', csrf.value)
    formData.append('bio', submittedBio)
    if (submittedAvatar) {
        formData.append('avatar', submittedAvatar)
    }

    saveBtn.disabled = true
    $.ajax({
        type: 'POST',
        url: '',
        data: formData,
        dataType: 'json',
        processData: false,
        contentType: false,
        cache: false,
        success: function(response){
            console.log(response)
            avatarImage.src = response.avatar
            avatarImage.alt = response.user
            if (bioInput.value === submittedBio) {
                bioInput.value = response.bio
            }
            if (submittedAvatar && avatarInput.files[0] === submittedAvatar) {
                avatarInput.value = ''
            }
            handleAlerts('success', 'your profile has been updated')
        },
        error: function(error){
            console.log(error)
            handleAlerts('danger', 'Your profile could not be updated.')
        },
        complete: function(){
            saveBtn.disabled = false
        }
    })
})
