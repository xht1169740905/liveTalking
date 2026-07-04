var pc = null;
var _speakingPollTimer = null;

function negotiate() {
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer().then((offer) => {
        return pc.setLocalDescription(offer);
    }).then(() => {
        // wait for ICE gathering to complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(() => {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then((response) => {
        return response.json();
    }).then((answer) => {
        document.getElementById('sessionid').value = answer.sessionid
        // 连接建立后开始轮询说话状态
        startSpeakingPoll();
        return pc.setRemoteDescription(answer);
    }).catch((e) => {
        alert(e);
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    if (document.getElementById('use-stun').checked) {
        config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
    }

    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', (evt) => {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    document.getElementById('start').style.display = 'none';
    negotiate();
    document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
    document.getElementById('stop').style.display = 'none';

    // 停止轮询
    stopSpeakingPoll();
    var btnInterrupt = document.getElementById('btn_interrupt');
    var statusEl = document.getElementById('speaking_status');
    if (btnInterrupt) btnInterrupt.style.display = 'none';
    if (statusEl) statusEl.style.display = 'none';

    // close peer connection
    setTimeout(() => {
        pc.close();
    }, 500);
}

// ============ 打断功能 ============

function interrupt() {
    var sessionid = document.getElementById('sessionid').value;
    console.log('Interrupting session: ' + sessionid);
    fetch('/interrupt_talk', {
        body: JSON.stringify({
            sessionid: String(sessionid),
        }),
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST'
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        console.log('Interrupt result:', data);
        if (data.code === 0) {
            var btnInterrupt = document.getElementById('btn_interrupt');
            var statusEl = document.getElementById('speaking_status');
            if (btnInterrupt) btnInterrupt.style.display = 'none';
            if (statusEl) statusEl.style.display = 'none';
        }
    }).catch(function(e) {
        console.error('Interrupt error:', e);
    });
}

// ============ 说话状态轮询 ============

function startSpeakingPoll() {
    // 先停掉旧的
    stopSpeakingPoll();
    // 每 200ms 轮询一次 is_speaking
    _speakingPollTimer = setInterval(checkSpeaking, 200);
}

function stopSpeakingPoll() {
    if (_speakingPollTimer) {
        clearInterval(_speakingPollTimer);
        _speakingPollTimer = null;
    }
}

function checkSpeaking() {
    var sessionid = document.getElementById('sessionid').value;
    if (!sessionid) return;
    fetch('/is_speaking', {
        body: JSON.stringify({
            sessionid: String(sessionid),
        }),
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST'
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        var speaking = data.data;  // true/false
        var btnInterrupt = document.getElementById('btn_interrupt');
        var statusEl = document.getElementById('speaking_status');
        if (speaking) {
            if (btnInterrupt) btnInterrupt.style.display = 'inline-block';
            if (statusEl) statusEl.style.display = 'block';
        } else {
            if (btnInterrupt) btnInterrupt.style.display = 'none';
            if (statusEl) statusEl.style.display = 'none';
        }
    }).catch(function(e) {
        // 忽略轮询错误
    });
}

window.onunload = function(event) {
    // 在这里执行你想要的操作
    stopSpeakingPoll();
    setTimeout(() => {
        pc.close();
    }, 500);
};

window.onbeforeunload = function (e) {
        stopSpeakingPoll();
        setTimeout(() => {
                pc.close();
            }, 500);
        e = e || window.event
        // 兼容IE8和Firefox 4之前的版本
        if (e) {
          e.returnValue = '关闭提示'
        }
        // Chrome, Safari, Firefox 4+, Opera 12+ , IE 9+
        return '关闭提示'
      }
