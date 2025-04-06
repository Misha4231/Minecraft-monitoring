const error_notification = document.querySelector('.body_error-notification')
const success_notification = document.querySelector('.body_success-notification')

document.querySelectorAll('.free_vote_button').forEach(function (voteButton){
    voteButton.addEventListener('click', function() {
        const vote_link = voteButton.dataset.link
        fetch(vote_link).then(response => response.json())
        .then(data => {
            if (data.error) {
                error_notification.textContent = data.error
                error_notification.style.display = 'block'
            } else{
                success_notification.textContent = 'You successfuly vote for a server'
                success_notification.style.display = 'block'
                const cur_diamonds = voteButton.parentElement.querySelector('.grey-text').textContent
                voteButton.parentElement.querySelector('.grey-text').textContent = parseInt(cur_diamonds) + 1
            }
           
            
            setTimeout(() => {
                error_notification.style.display = 'none'
                success_notification.style.display = 'none'
            },3500)
        })
    })
    
})