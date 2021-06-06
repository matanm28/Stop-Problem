const passButton = document.getElementById('pass-btn');
const acceptButton = document.getElementById('accept-btn');
const currentNumber = document.getElementById('current-number');


function onPageLoad() {
    let current_index = 0;
    let passButtonLocked = false;
    const {id: seq_id, values} = get_sequence();
    const {id: player_id, is_done} = get_player()
    let timestamps = [Date.now()]
    $(passButton).on('click', () => {
        timestamps.push(Date.now());
        if (current_index + 1 < values.length) {
            currentNumber.innerHTML = `${values[++current_index].value}`;
        }
        if (!passButtonLocked && current_index + 1 === values.length) {
            $(this).prop('disabled', true);
            passButton.classList.replace('btn-warning', 'btn-light');
            passButtonLocked = true;
        }
    });
    $(acceptButton).on('click', () => {
        timestamps.push(Date.now());
        let data = {
            'seq_id': seq_id,
            'time_stamps': timestamps,
            'chosen_index': current_index,
            'player_id': player_id,
        };
        const headers = new Headers({
            'Content-Type': 'application/x-www-form-urlencoded',
        });
        $.ajax({
            url: '',
            dataType: 'json',
            type: 'post',
            data: {
                'seq_id': seq_id,
                'time_stamps': timestamps,
                'chosen_index': current_index,
                'player_id': player_id,
                'is_accepted': !$(passButton).is(':disabled'),
            },
            success: function (json) {
                if (json['has_next']) {
                    window.location.reload();
                } else {
                    window.location.pathname = 'thanks-for-playing';
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest, textStatus, errorThrown);
            }
        });

    });
}


$(window).on('DOMContentLoaded', onPageLoad);

