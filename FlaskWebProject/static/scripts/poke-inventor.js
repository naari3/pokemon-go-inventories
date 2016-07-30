$(function () {
  $table = $("table");
  $progress = $("#progress");
  $submit = $("#submit");
  $form = $("#form");

  $table.hide();
  $progress.hide();

  function addPokemons(pokemons) {
    for (var poke of pokemons) {
      if (!(poke.stamina)) { poke.stamina = "" }
      if (!(poke.nickname)) { poke.nickname = "" }
      var $newtr = $("<tr></tr>");
      $newtr.append(`<td>${poke.cp}</td>`);
      $newtr.append(`<td>${poke.name}</td>`);
      $newtr.append(`<td>${poke.individual_attack}</td>`);
      $newtr.append(`<td>${poke.individual_defense}</td>`);
      $newtr.append(`<td>${poke.individual_stamina}</td>`);
      // $newtr.append(`<td>${poke.power_quotient}</td>`);
      $newtr.append(`<td>${poke.move_1}</td>`);
      $newtr.append(`<td>${poke.move_2}</td>`);
      $newtr.append(`<td>${poke.stamina}</td>`);
      $newtr.append(`<td>${poke.nickname}</td>`);
      $table.append($newtr);
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
          pokemons = response.ResultSet;
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
});
