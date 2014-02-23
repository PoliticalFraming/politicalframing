'use strict';

$(document).ready(function(){
  var BOSH_SERVICE = 'http://chat.politicalframing.com:5280/http-bind';
  var JABBER_HOST  = 'chat.politicalframing.com';
  var ADMIN_USER   = 'atul@chat.politicalframing.com';
  var connection = null;
  var username   = null;

  var add_chatbox = function() {
    $('body').append('<div id="converse-chat"></div>');
    var domContent = [
      '<div class="converse-menu">Click for live chat</div>',
      '<div class="converse-chatbox" style="display: none;">',
      '    <div class="converse-conversation">',
      '    </div>',
      '    <div class="converse-chat-input">',
      '        <input type="text" name="chat_text" id="converse-chat-input" placeholder="Type here and hit <enter> to chat">',
      '    </div>',
      '<div id="converse-status"></div>',
      '</div>',
    ].join('');
    $('#converse-chat').append(domContent);

  };

  var scrollToBottom = function(selector){
    var divHeight = $(selector).height();
    var divOffset = $(selector).offset().top;
    var windowHeight = $(window).height();
    $('html,body').animate({
      scrollTop: divOffset-windowHeight+divHeight
    },'slow');
  }

  var add_listeners = function() {
    $('#converse-chat .converse-menu').click(toggleChat);
    $('#converse-chat .converse-chat-input input').bind('keypress', function(e) {
      var code = (e.keyCode ? e.keyCode : e.which);
      if(code == 13) { //Enter keycode
        var content = $(this).val();
        $(this).val("");
        send_message(content);
      }
     }); 
  };

  var log = function(msg) { $('#converse-status').html(msg); };

  function onMessage(msg) {
    console.log(msg);
    var to = msg.getAttribute('to');
    var from = msg.getAttribute('from');
    var type = msg.getAttribute('type');
    var elems = msg.getElementsByTagName('body');

    if (type == 'chat' && elems.length > 0) {
      var body = elems[0];
      appendMessage(from,  Strophe.getText(body));
    }

    return true;
  }

  function send_message(msg) {
    var message_xml = Strophe.xmlElement('body', {}, msg)
    var reply = $msg({to: ADMIN_USER, from: username, type: 'chat'}).cnode(Strophe.copyElement(message_xml));
    appendMessage('Me',  msg, 'converse-self');
    connection.send(reply.tree());
    var objDiv = document.getElementsByClassName('converse-conversation')[0];
    objDiv.scrollTop = objDiv.scrollHeight;
  }


  var onConnect = function(status) {
    if (status === Strophe.Status.CONNECTING) {
      log('Connecting..');
    } else if (status === Strophe.Status.CONNFAIL) {
      log('Failed to connect.');
      $('#connect').get(0).value = 'connect';
    } else if (status === Strophe.Status.DISCONNECTING) {
      log('Disconnecting.');
    } else if (status === Strophe.Status.DISCONNECTED) {
      log('Disconnected.');
      $('#connect').get(0).value = 'connect';
    } else if (status === Strophe.Status.CONNECTED) {
      log('Connected');
      connection.addHandler(onMessage, null, 'message', null, null,  null);
      connection.send($pres().tree());
    }
  };

  var appendMessage = function(person, messageContent, className) {
    className = className ? className : '';
    person = person.split('@')[0];

    var messageDom = [
      '<div class="converse-msg ' + className + '">',
      '  <span class="converse-user">' + person + ':</span>&nbsp;&nbsp;<span class="converse-txt">' + messageContent + '</span>',
      ' </div>'
    ].join('');

    $('.converse-conversation').append(messageDom);
    scrollToBottom('.converse-conversation');
  };

  var connectXMPP = function() {
    connection = new Strophe.Connection(BOSH_SERVICE);
    /* You can include your app user name here */
    username = 'user' + Math.floor(Math.random() * 100000) + '@' + JABBER_HOST;
    connection.connect( username, 'dummy', onConnect);
  };


  var toggleChat = function() {
    $('.converse-chatbox').toggle();
  };

  var init = function() {
    connectXMPP();
    add_chatbox();
    add_listeners();
  };


 /* Initialize */

 init();
 

});
