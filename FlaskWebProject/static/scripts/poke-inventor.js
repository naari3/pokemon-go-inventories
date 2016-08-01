$(function () {
  var $table = $("table");
  var $progress = $("#progress");
  var $submit = $("#submit");
  var $form = $("#form");

  $table.hide();
  $progress.hide();

  $table.stupidtable();

  type2int = {
    "Normal":1, "Fire":2, "Water":3, "Electric":4, "Grass":5, "Ice":6,
    "Fighting":7, "Poison":8, "Ground":9, "Flying":10, "Psychic":11, "Bug":12,
    "Rock":13, "Ghost":14, "Dragon":15, "Dark":16, "Steel":17,"Fairy":18,
  }

  function addPokemons(pokemons) {
    var i = 0;
    for (var poke of pokemons) {
      if (!(poke.stamina)) { poke.stamina = "" }
      if (!(poke.nickname)) { poke.nickname = "" }
      var move_1_type_value = type2int[poke.move_1_type];
      var move_2_type_value = type2int[poke.move_2_type];
      var $newtr = $(`<tr data-id="${poke._id}"></tr>`);
      $newtr.append(`<td>${poke.pokemon_id}</td>`);
      $newtr.append(`<td><img class="left icon" src="/static/icons/${poke.pokemon_id}.png"></i>${poke.name}</td>`);
      $move1td = $(`<td class="move type ${poke.move_1_type}" data-sort-value="${move_1_type_value}">${poke.move_1} </td>`);
      $move2td = $(`<td class="move type ${poke.move_2_type}" data-sort-value="${move_2_type_value}">${poke.move_2} </td>`);
      $move1td.append(`<span class="dps small">[${poke.move_1_DPS}]</span>`);
      $move2td.append(`<span class="dps small">[${poke.move_2_DPS}]</span>`);
      $newtr.append($move1td);
      $newtr.append($move2td);
      $newtr.append(`<td>${poke.cp}</td>`);
      $newtr.append(`<td>${poke.individual_attack}</td>`);
      $newtr.append(`<td>${poke.individual_defense}</td>`);
      $newtr.append(`<td>${poke.individual_stamina}</td>`);
      $newtr.append(`<td>${poke.power_quotient}</td>`);
      $newtr.append(`<td>${poke.stamina}</td>`);
      $nicktd = $(`<td><span data-id="${poke._id}">${poke.nickname}</span></td>`);
      $nicktd.append(`<i class="material-icons right nickname">edit</i>`);
      $newtr.append($nicktd);
      $newtr.append(`<td><input type="checkbox" class="filled-in fav" id="fav${i}" ${(poke.favorite === 1 ? "checked=\"checked\"" : "")}/><label for="fav${i}"></label></td>`);
      $table.append($newtr);
      i++;
    }
  }

  $submit.click(function () {
    var username = $("#username").val();
    var password = $("#password").val();
    var auth_service = $(':radio[name="auth_service"]:checked').val();
    if (username && password && auth_service) {
      $(this).prop('disabled', true);
      $.ajax({
        type: "POST",
        url: "/rcv",
        data: {
          username: username,
          password: password,
          auth_service: auth_service,
        }
      }).done(function (response) {
        console.log(response);
        if (response.ResultSet) {
          var pokemons = response.ResultSet;
          addPokemons(pokemons);
          $progress.fadeOut(250, function () {
            $form.hide();
            $table.fadeIn(250);
          });
        } else {
          Materialize.toast($('<span><i class="material-icons right">warning</i>login error</span>'), 2000,'',
          function(){
            location.reload()
          });
        }
      }).fail(function(data, textStatus, errorThrown){
        // alert(textStatus);
        Materialize.toast($(`<span><i class="material-icons right">warning</i>${textStatus}</span>`), 2000,'',
        function(){
          location.reload()
        });
      });
      // console.log(errorThrown.message);
      $progress.fadeIn(250);
    } else {
      Materialize.toast($('<span><i class="material-icons right">warning</i>全て入力して下さい</span>'), 4000);
    }
  });

  $(document).on('click', '.nickname', function () {
    // console.dir($(this));
    var $parent = $(this).parent();
    var $span = $($parent.find('span')[0]);
    var nickname = $span.text();
    $span.hide();
    $(this).hide();
    if ($parent.find('.nickname_input')[0]) {
      $($parent.find('.nickname_input')[0]).show();
      $($parent.find('.nickname_save')[0]).show();
    } else {
      $parent.append(`<input class="nickname_input" type="text" value=${nickname}></input>`);
      $parent.append(`<i class="material-icons prefix nickname_save">save</i>`);
    }
  });

  $(document).on('click', '.nickname_save', function () {
    var id = $(this).parent().parent().data('id').toString();
    var $parent = $(this).parent();
    var $span = $($parent.find('span')[0]);
    var $nickedit = $($parent.find('.nickname')[0]);
    var $nick_input = $($parent.find('.nickname_input')[0]);
    var nickname = $nick_input.val();
    $span.text(nickname);
    $nick_input.hide();
    $(this).hide();
    $span.show();
    $nickedit.show();
    $.ajax({
      type: "POST",
      url: "/rename",
      data: {
        pokeid: id,
        pokename: nickname,
      }
    }).done(function (response) {
      console.log(response);
    }).fail(function(data, textStatus, errorThrown){
      // alert(textStatus);
      Materialize.toast($(`<span><i class="material-icons right">warning</i>${textStatus}</span>`), 2000,'',
      function () {
        location.reload();
      });
    });
  });

  $(document).on('change', '.fav', function () {
    var id = $(this).parent().parent().data('id').toString();
    $.ajax({
      type: "POST",
      url: "/favorite",
      data: {
        pokeid: id,
        is_favorite: $(this).prop('checked').toString(),
      }
    }).done(function (response) {
      console.log(response);
    }).fail(function(data, textStatus, errorThrown){
      // alert(textStatus);
      Materialize.toast($(`<span><i class="material-icons right">warning</i>${textStatus}</span>`), 2000,'',
      function () {
        location.reload();
      });
    });
  });
});
