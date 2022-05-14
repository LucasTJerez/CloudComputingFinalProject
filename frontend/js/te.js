var pos = [];
var neg = [];
var mix = [];
var neu = [];
var all_reviews = [];

selected_product = localStorage.getItem("product");
e = localStorage.getItem("e");
target_id = localStorage.getItem("target_id");
product_list = localStorage.getItem("product_list");
price = localStorage.getItem("price");
image = localStorage.getItem("image");
name_p = localStorage.getItem("name");
storefront = localStorage.getItem("storefront");

var apigClient = apigClientFactory.newClient();
var params = {
    productName: selected_product,
};
var div = document.getElementById("product_list");
div.innerHTML = `<h3>Loading review data...</h3>`;

apigClient.searchreviewsGet(params, {}, {}).then(function (result) {
    div.innerHTML = ``;
    data = result.data;
    sources = new Map();

    for (let i = 0; i < data.review_contents.length; i++) {
        review_content = result.data.review_contents[i];
        src = review_content.source.toUpperCase();
        sources.set(src, true);
        if (review_content.sentiment.Sentiment == "POSITIVE") {
            pos.push(review_content);
        }
        if (review_content.sentiment.Sentiment == "NEGATIVE") {
            neg.push(review_content);
        }
        if (review_content.sentiment.Sentiment == "NEUTRAL") {
            neu.push(review_content);
        }
        if (review_content.sentiment.Sentiment == "MIXED") {
            mix.push(review_content);
        }
    }

    score =
        (data.pro_count + 0.5 * data.mixed_count) /
        (data.pro_count + data.con_count + data.mixed_count);
    n_stars = parseInt(score * 10);
    content = "";
    product = product_list[parseInt(target_id)];
    console.log(product);

    var detailsContent = document.getElementById("details");

    detailsContent.innerHTML = `  
    
    <div class="card">
    <div class="product-imgs">
         <div class="img-display">
            <div class="img-showcase">
              <img width="80" 
              height="50" 
                src="${image}"/>
            </div>
          </div>
          </div>

          <div class="product-content">
          <div >
            <h3>
              ${name_p}
            </h3>
          </div>
          <div class="product-rating">
            <p>
              DoubleCheck's Score: ${n_stars}/10\n
            </p>
            <p>
            number of reviews: ${data.review_contents.length}
            </p>
          </div>
          <div class="product-price">
            <p>
              Price: ${price}\n
            </p>
            <a  class="product-link" href="${storefront}"> link to storefront </a>
            </div>
            </div>
  
          `;

    div.innerHTML += content;
    for (let i = 0; i < data.review_contents.length; i++) {
        review_content = result.data.review_contents[i];

        if (review_content.source.toUpperCase() == "AMAZON") {
            img_src = "https://pngimg.com/uploads/amazon/amazon_PNG27.png";
        }
        if (review_content.source.toUpperCase() == "REDDIT") {
            img_src = "https://www.redditinc.com/assets/images/site/reddit-logo.png";
        }

        div.innerHTML += `
            <li style="list-style: none;">

             

                <img class="reviewImage" 
                src="${img_src}" 
                />
                <p> 
                  ${review_content.source.toUpperCase()}
                </p>
                <p>
                <a href="${review_content.link}">link to review</a>
                </p>

                <div class="product_content">
                  <ul class="list_height" style="list-style: none;">
                    <li style="list-style: none;">
                    <p>
                      ${review_content.sentiment.Sentiment}
                      </p>
                    </li>
                    <li style="list-style: none;">
                      <p style="height:100px; overflow:scroll;">
                      ${review_content.review}
                      </p>
                    </li>
                  <ul>
                  </div>
            </li>
            </div>`;
    }

    div.innerHTML += `</ul>`;
});
