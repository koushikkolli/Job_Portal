$(document).ready(function(){
  //get the data from the server for display
  $.ajax({
    type: 'GET',
    url: '/get_data',
    cache: "False",
    success: function(resp){

      //data from response
      var key_data = JSON.parse(resp);

      //get elemnts doc to change the element type
      job_type = document.getElementById('keywords');
      job_loc = document.getElementById('locations');

      //loop over every element and add to datalist
      key_data['keys'].forEach(function(item){

        //create the option for data list
        var option = document.createElement('option');

        // add the value
        option.value = item;

        //append the data
        job_type.appendChild(option);
      });

      key_data['locs'].forEach(function(item){

        //create the option for data list
        var option = document.createElement('option');

        // add the value
        option.value = item;

        //append the data
        job_loc.appendChild(option);
      });

    },
    error: function(resp){
      console.log("Error");
    },
  });
});

function search_job(){
  var key = document.getElementById("key").value;
  var loc = document.getElementById("loc").value;

  var key_check=true;
  var loc_check=true;

  if (key == ""){
    $("#errkey")
    .text("Please enter job type")
    .show()
    .fadeOut(4000);
    key_check=false;
  }
  if(loc == ""){
    $("#errloc")
    .text("Please enter location")
    .show()
    .fadeOut(4000);
    loc_check=false;
    return;
  }

  if (key_check && loc_check){
    var data = {
      job: key,
      location: loc
    }
    $.ajax({
      type: 'POST',
      url: '/fetch_jobs',
      data: data,
      cache: false,
      success: function(resp){
        if(resp){
          if (resp['result'] == '1'){
            var jdata = JSON.parse(resp['data']);
            var len = Object.keys(jdata['Company']).length;

            var main = document.getElementById('display_tab');
            main.innerHTML= "";
            for (var i = 0; i < len; i+=1){
              var row_tag = document.createElement('div');
              row_tag.className = "row mr-4";

              for (var j = 0; j < 3; j+=1){
                if (i < len){

                  var col_tag = document.createElement('div');
                  col_tag.className = "col-lg-4 col-md-4 col-sm-6 col-xs-12 d-flex align-items-stretch";
                  var card_tag = document.createElement('div');
                  card_tag.className = "card card-cascade wider";
                  var card_head = document.createElement('h5');
                  card_head.className = "card-header";
                  card_head.textContent = jdata['Company'][i];
                  card_tag.appendChild(card_head);
                  var ul = document.createElement('ul');
                  ul.className = "list-group list-group-flush";
                  var li1 = document.createElement('li');
                  li1.className = "list-group-item";
                  li1.textContent = jdata['Job_title'][i];

                  var li2 = document.createElement('li');
                  li2.className = "list-group-item";
                  li2.textContent = jdata['Location'][i];

                  ul.appendChild(li1);
                  ul.appendChild(li2);

                  card_tag.appendChild(ul);

                  var body_tag = document.createElement('div');
                  body_tag.className = "card-body";
                  var p_tag = document.createElement('p');
                  p_tag.className = "card-text text-muted";
                  p_tag.textContent = jdata['Summary'][i];
                  body_tag.appendChild(p_tag);

                  var a_tag = document.createElement('a');
                  a_tag.className = "btn btn-primary";
                  a_tag.href = jdata['Apply site'][i];
                  a_tag.textContent = "Apply";
                  body_tag.appendChild(a_tag);

                  card_tag.appendChild(body_tag);

                  var foot = document.createElement('div');
                  foot.className = "card-footer text-muted text-center";
                  foot.textContent = jdata['Date'][i];

                  card_tag.appendChild(foot);

                  col_tag.appendChild(card_tag);

                  row_tag.appendChild(col_tag);
                  i+=1;
                }
                else{
                  break;
                }
              }
              i-=1
              main.appendChild(row_tag);
            }
          }
          else if(resp['result'] == '0'){
            $('#fetch_err')
            .text(resp['msg'])
            .show()
            .fadeOut(10000);
          }
          else{
            $('#fetch_err')
            .text("No jobs available for this selection try to change location and search")
            .show()
            .fadeOut(10000);
          }
        }
        else{
          $('#fetch_err')
          .text("Something Went wrong")
          .show();
        }
      },
      error: function(request, status, error){}
    });
  }

}
