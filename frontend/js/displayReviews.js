var queryString = window.location.search;
var parameters = new URLSearchParams(queryString);
// var productName = parameters.get("query");
var apigClient = apigClientFactory.newClient();

var selected_product = "";
var pos = [];
var neg = [];
var mix = [];
var neu = [];
var all_reviews = [];
product_list = [];

var params = {
  productName: parameters.get("query"),
};
var div = document.getElementById("product_list");
div.innerHTML = `<h3>Fetching products...</h3>`;

apigClient.searchproductsGet(params, {}, {}).then(function (result) {
  div.innerHTML = `<ul style="list-style: none" class="main">`;
  console.log(result.data.length);
  if (result.data.length == 0) {
    div.innerHTML = `<h3>Sorry we do not have this product in our database:(...</h3>`;
  }
  product_list = result.data;
  for (let i = 0; i < result.data.length; i++) {
    product = result.data[i];
    console.log(product.price);
    if (product.price != null )
    {
      div.innerHTML += `<li style="list-style: none;">
      <div class="card">
          <img style="margin:4px; padding-left:14px; width:28%; padding-bottom:14px; padding-top:14px;"
           src="${product.image[0]}"/>

          <ul style="list-style: none;">
            <li style="list-style: none;">
              <button style="border: none; font-family: Georgia, serif; font-size: 20px; color: #1aa89b; 
              background: none;" id="${i}" onclick="goToDetails(event)">${product.productName}</button>
            </li>
            <li style="list-style: none;  color:#1aa89b; ">
              <h4>${product.price}</h4>
            </li>
          <ul>

      </div>
    </li>`;

    }
    
    // name="${product.price}" value="${product.storefront}
    // console.log(product)
  }
  div.innerHTML += "</ul>";
});

function goToDetails(e){
  //rest of the code
  console.log(e.target.id);
  selected_product = e.path[0].innerHTML
  target_id = parseInt(e.target.id);
  console.log(target_id);
  console.log(product_list[target_id]);

  localStorage.setItem("price", product_list[target_id]['price']);
  localStorage.setItem("image", product_list[target_id]['image'][0]);
  localStorage.setItem("brand", product_list[target_id]['brand']);
  localStorage.setItem("details", product_list[target_id]['productName']);
  localStorage.setItem("storeFront", product_list[target_id]['storefront']);
  // product_list = localStorage.setItem('product_list' , product_list);
  // localStorage.setItem('product', selected_product);
  // localStorage.setItem('target_id', parseInt(target_id));
  document.location.href='details.html';
  // console.log("let's get this party started");


};
