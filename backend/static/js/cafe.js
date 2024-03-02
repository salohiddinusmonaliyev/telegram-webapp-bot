(function ($) {
    $.fn.redraw = function () {
        return this.map(function () {
            this.offsetTop;
            return this;
        });
    };
})(jQuery);

var Cafe = {
    canPay: false,
    modeOrder: false,
    totalPrice: 0,

    init: function (options) {
        Telegram.WebApp.ready();
        Cafe.apiUrl = options.apiUrl;
        Cafe.userId = options.userId;
        Cafe.userHash = options.userHash;
        Cafe.initLotties();
        $("body").show();
        if (
            !Telegram.WebApp.initDataUnsafe ||
            !Telegram.WebApp.initDataUnsafe.query_id
        ) {

        }
        $(".js-item-lottie").on("click", Cafe.eLottieClicked);
        $(".js-item-incr-btn").on("click", Cafe.eIncrClicked);
        $(".js-item-decr-btn").on("click", Cafe.eDecrClicked);
        $(".js-order-edit").on("click", Cafe.eEditClicked);
        $(".js-status").on("click", Cafe.eStatusClicked);
        $(".js-order-comment-field").each(function () {
            autosize(this);
        });
        Telegram.WebApp.MainButton.setParams({
            text_color: "#fff",
        }).onClick(Cafe.mainBtnClicked);
        initRipple();
    },
    initLotties: function () {
        $(".js-item-lottie").each(function () {
            RLottie.init(this, {
                maxDeviceRatio: 2,
                cachingModulo: 3,
                noAutoPlay: true,
            });
        });
    },

    eIncrClicked: function (e) {
        e.preventDefault();
        var itemEl = $(this).parents(".js-item");
        Cafe.incrClicked(itemEl, 1);
    },
    eDecrClicked: function (e) {
        e.preventDefault();
        var itemEl = $(this).parents(".js-item");
        Cafe.incrClicked(itemEl, -1);
    },
    
    getOrderItem: function (itemEl) {
        var id = itemEl.data("item-id");
        return $(".js-order-item").filter(function () {
            return $(this).data("item-id") == id;
        });
    },
    updateItem: function (itemEl, delta) {
        var price = +itemEl.data("item-price");
        var count = +itemEl.data("item-count") || 0;
        var counterEl = $(".js-item-counter", itemEl);
        counterEl.text(count ? count : 1);
        var isSelected = itemEl.hasClass("selected");
        if (!isSelected && count > 0) {
            $(".js-item-lottie", itemEl).each(function () {
                RLottie.playOnce(this);
            });
        }
        var anim_name = isSelected
            ? delta > 0
                ? "badge-incr"
                : count > 0
                    ? "badge-decr"
                    : "badge-hide"
            : "badge-show";
        var cur_anim_name = counterEl.css("animation-name");
        if (
            (anim_name == "badge-incr" || anim_name == "badge-decr") &&
            anim_name == cur_anim_name
        ) {
            anim_name += "2";
        }
        counterEl.css("animation-name", anim_name);
        itemEl.toggleClass("selected", count > 0);

        var orderItemEl = Cafe.getOrderItem(itemEl);
        var orderCounterEl = $(".js-order-item-counter", orderItemEl);
        orderCounterEl.text(count ? count : 1);
        orderItemEl.toggleClass("selected", count > 0);
        var orderPriceEl = $(".js-order-item-price", orderItemEl);
        var item_price = count * price;
        orderPriceEl.text(Cafe.formatPrice(item_price));

        Cafe.updateTotalPrice();
    },
    incrClicked: function (itemEl, delta) {
        if (Cafe.isLoading || Cafe.isClosed) {
            return false;
        }
        var count = +itemEl.data("item-count") || 0;
        count += delta;
        if (count < 0) {
            count = 0;
        }
        itemEl.data("item-count", count);
        Cafe.updateItem(itemEl, delta);
    },


};
