const passButton = document.getElementById('pass-btn');
const acceptButton = document.getElementById('accept-btn');
const currentNumber = document.getElementById('current-number');

function changeCurrentNumber(newNumber) {
    currentNumber.innerHTML = `${newNumber}`;
}

function lockPassButton() {
    $(passButton).prop('disabled', true);
    passButton.classList.replace('btn-warning', 'btn-light');
    pageState.passButtonLocked = true;
}

function onPageLoad() {
    loadState();
    $(passButton).on('click', () => {
        pageState.timestamps.push(Date.now());
        if (pageState.currentIndex + 1 < pageState.values.length) {
            changeCurrentNumber(pageState.values[++pageState.currentIndex].value);
        }
        if (!pageState.passButtonLocked && pageState.currentIndex + 1 === pageState.values.length) {
            lockPassButton();
        }
    });
    $(acceptButton).on('click', () => {
        pageState.timestamps.push(Date.now());
        $(window).off('beforeunload', confirmReloadAndSaveState);
        $.ajax({
            url: '',
            dataType: 'json',
            type: 'post',
            data: {
                'seq_id': pageState.seqId,
                'time_stamps': pageState.timestamps,
                'chosen_index': pageState.currentIndex,
                'player_id': pageState.playerId,
                'is_accepted': !$(passButton).is(':disabled'),
            },
            success: function (json) {
                if (json['has_next']) {
                    window.location.reload();
                } else {
                    window.location.pathname = 'thanks-for-playing'
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest, textStatus, errorThrown);
            }
        });
        clearState();
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const beforeUnloadListener = (event) => {
    event.preventDefault();
    return event.returnValue = "Are you sure you want to exit?";
};

let pageState = {
    currentIndex: 0,
    passButtonLocked: false,
    seqId: null,
    timestamps: null,
    values: null,
    playerId: null,
};

function saveState() {
    const savedStateJsonString = JSON.stringify(pageState);
    window.sessionStorage.setItem('state', savedStateJsonString);
    console.log('Page state saved successfully!');
}

function loadState() {
    let savedState = window.sessionStorage.getItem('state')
    if (savedState === null) {
        console.log('No saved state - initializing page state.')
        const {id, values} = get_sequence();
        pageState.seqId = id;
        pageState.values = values;
        pageState.timestamps = [Date.now()];
        pageState.playerId = get_player()['id']
        console.log('Page state initialized successfully!');
    } else {
        pageState = JSON.parse(savedState);
        changeCurrentNumber(pageState.values[pageState.currentIndex].value);
        if (pageState.passButtonLocked) {
            lockPassButton();
        }
        console.log('Page state loaded successfully!');
    }
}

function clearState() {
    window.sessionStorage.removeItem('state');
    console.log('Page state cleared successfully!');
}

function confirmReloadAndSaveState(event) {
    event.preventDefault();
    saveState();
}

$(window).on('beforeunload', confirmReloadAndSaveState);


$(window).on('DOMContentLoaded', onPageLoad);

