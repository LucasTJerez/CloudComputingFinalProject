var pos = [];
var neg = [];
var mix = [];
var neu = [];
var all_reviews = [];

// console.log(selected_product);
// // e = localStorage.getItem("e");
// target_id = localStorage.getItem("target_id");
// product_list = localStorage.getItem("product_list");
price = localStorage.getItem("price");
image = localStorage.getItem("image");
brand = localStorage.getItem("brand");
details = localStorage.getItem("details");
storefront = localStorage.getItem("storeFront");

var apigClient = apigClientFactory.newClient();
var params = {
    productName: details,
}


var div = document.getElementById("loading");
div.innerHTML = `<h3>Loading review data...</h3>`;

apigClient.searchreviewsGet(params, {}, {}).then(function (result) {
    div.innerHTML = ``;
    data = result.data;
    sources = new Map();

    console.log(data.review_contents);
    console.log(data.review_contents.length);

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
    // product = product_list[parseInt(target_id)];
    // console.log(product);

    var detailsContent = document.getElementById("details");

    detailsContent.innerHTML = `  
    <div class="card-wrapper">
    <div class="card">
    <div class="product-imgs">
         <div class="img-display">
            <div class="img-showcase">
              <img 
                src="${image}"/>
            </div>
          </div>
          </div>

          <div class="product-content">

            <h3>
              ${brand}
            </h3>

          <div class="product-rating">
            <p >
              DoubleCheck's Score: ${n_stars}/10\n
            </p>
            <p>
            number of reviews: ${data.review_contents.length}
            </p>
          </div>
          <div class="product-price">
            <p style="color: #1aa89b;">
              Price: ${price}\n
            </p>
            <a  class="product-link" href="${storefront}"> link to storefront </a>
            </div>

            <div class="product-detail">
            <h2 style="color: #1aa89b;">about this brand:</h2>
            <p style="color: #1aa89b;">
              ${details}
            </p>
          </div>
          `;


    for (let i = 0; i < data.review_contents.length; i++) {
        review_content = result.data.review_contents[i];
        console.log(review_content.sentiment.Sentimen)

        if (review_content.source.toUpperCase() == "AMAZON") {
            img_src = "https://pngimg.com/uploads/amazon/amazon_PNG27.png";
        }
        if (review_content.source.toUpperCase() == "REDDIT") {
            img_src = "https://www.redditinc.com/assets/images/site/reddit-logo.png";
        }
        if (review_content.source.toUpperCase() == "WALMART"){
          img_src = "https://i.ibb.co/ssP2jL0/walmart.png"
        };


        if (review_content.sentiment.Sentiment == "POSITIVE") {
            img_sentiment = "https://i.ibb.co/r2hbyLC/positive.png"
        }
        if (review_content.sentiment.Sentiment == "NEGATIVE") {
            img_sentiment = "https://i.ibb.co/Xpddywj/negative.png"
        }
        if (review_content.sentiment.Sentiment == "NEUTRAL") {
            img_sentiment = "https://i.ibb.co/8xMhR9h/mixed.png"
        }
        if (review_content.sentiment.Sentiment == "MIXED") {
            img_sentiment ="https://img.myloview.com/posters/poker-face-emoji-isolated-on-white-background-neutral-face-emoticon-symbol-modern-simple-vector-icon-for-website-design-mobile-app-ui-vector-illustration-400-206538609.jpg"
            
        }

        detailsContent.innerHTML += `
        <div class="reviewsCard">
            <li style="list-style: none; margin:2px;">
                <img style="margin:2px;" class="reviewImage" 
                src="${img_src}" 
                />
                <p style="margin:2px; font-family:Monospace; ">
                <a href="${review_content.link}">More details</a>
                </p>
                  <ul class="list_height" style="list-style: none;">
                    <li style="list-style: none;">
                    <img style="width:35px;" src="${img_sentiment}" />
                    </li>
                    <li style="list-style: none;">
                      <p id="scroll" style="height:120px; padding-top: 35px;
                      padding-bottom: 20px; overflow:scroll !important; font-family:Monospace; "  >
                      ${review_content.review}
                      </p>
                    </li>
                  <ul>
            </li>
            </div>
            </div>
            </div>
            </div>`;
    }

    detailsContent.innerHTML += `</ul>`;
});
