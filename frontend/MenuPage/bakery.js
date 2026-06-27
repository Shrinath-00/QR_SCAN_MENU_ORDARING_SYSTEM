var params = new URLSearchParams(window.location.search);
var TABLE_ID = params.get('table');
if (!TABLE_ID) {
  TABLE_ID = '1';
}
var ORDER_SIG = params.get('sig');
if (!ORDER_SIG) {
  ORDER_SIG = '';
}

var MENU_DATA = [];
var cart = {};

try {
  var saved = localStorage.getItem('guest_cart');
  if (saved) {
    cart = JSON.parse(saved);
  }
} catch(e) {
  console.log('failed to load cart', e);
}

function getItemCalories(name) {
  var sum = 0;
  for (var i = 0; i < name.length; i++) {
    sum += name.charCodeAt(i);
  }
  return (sum % 280) + 120 + ' Calories';
}

function isVegItem(name) {
  var n = name.toLowerCase();
  var nonVegKeywords = ['chicken', 'egg', 'fish', 'meat', 'mutton', 'kebab', 'beef', 'pork', 'prawn', 'shrimp', 'salmon', 'pepperoni', 'salami', 'bacon', 'ham'];
  for (var i = 0; i < nonVegKeywords.length; i++) {
    if (n.indexOf(nonVegKeywords[i]) !== -1) {
      if (n.indexOf('veg kebab') !== -1) return true;
      if (n.indexOf('eggless') !== -1) return true;
      return false;
    }
  }
  return true;
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('table-number-label').textContent = 'Table ' + TABLE_ID;

  document.getElementById('products-grid').innerHTML =
    '<div class="text-center py-10">' +
    '<div class="w-6 h-6 border-2 border-brandRed border-t-transparent rounded-full animate-spin mx-auto"></div>' +
    '<p class="text-xs text-gray-400 mt-3">Loading bakery items...</p>' +
    '</div>';

  CONFIG.loadCafeConfig().then(function() {
    loadBakeryMenu();
  });
});

function loadBakeryMenu() {
  fetch(CONFIG.API_URL + '/api/menu', {
    headers: { 'ngrok-skip-browser-warning': 'true' }
  })
    .then(function (r) {
      if (!r.ok) {
        throw new Error(r.status);
      }
      return r.json();
    })
    .then(function (data) {
      if (data.categories) {
        MENU_DATA = data.categories;
      } else {
        MENU_DATA = [];
      }
      renderBakeryProducts();
      updateCartBadge();
    })
    .catch(function (err) {
      console.log('menu fetch failed', err);
      document.getElementById('products-grid').innerHTML =
        '<div class="text-center py-10">' +
        '<p class="text-sm text-red-400">⚠️ Failed to load bakery items.</p>' +
        '<button onclick="location.reload()" class="mt-3 text-xs underline text-gray-500">Try again</button>' +
        '</div>';
    });
}

function renderBakeryProducts() {
  var grid = document.getElementById('products-grid');
  var hits = [];

  for (var i = 0; i < MENU_DATA.length; i++) {
    var cat = MENU_DATA[i];
    for (var j = 0; j < cat.items.length; j++) {
      var item = cat.items[j];
      var catName = cat.name.toLowerCase();
      var itemName = item.name.toLowerCase();
      
      var isBakery = catName.indexOf('dessert') !== -1 ||
                     itemName.indexOf('cake') !== -1 ||
                     itemName.indexOf('brownie') !== -1 ||
                     itemName.indexOf('cheesecake') !== -1 ||
                     itemName.indexOf('croissant') !== -1 ||
                     itemName.indexOf('pastry') !== -1 ||
                     itemName.indexOf('muffin') !== -1 ||
                     itemName.indexOf('donut') !== -1 ||
                     itemName.indexOf('roll') !== -1 ||
                     itemName.indexOf('pancake') !== -1;

      if (isBakery) {
        hits.push({ item: item, catId: cat.id, idx: j });
      }
    }
  }

  if (hits.length === 0) {
    grid.innerHTML = '<p class="text-center text-sm text-gray-400 py-10">No bakery items available right now.</p>';
    return;
  }

  var html = '';
  for (var k = 0; k < hits.length; k++) {
    html += productCardHtml(hits[k].item, hits[k].catId, hits[k].idx);
  }
  grid.innerHTML = html;
}

function productCardHtml(item, catId, idx) {
  var key = 'p:' + catId + ':' + idx;
  var qty = 0;
  if (cart[key]) {
    qty = cart[key].qty;
  }
  var currency = CONFIG.cafe ? CONFIG.cafe.currency_symbol : '₹';
  var isVeg = isVegItem(item.name);
  var calories = getItemCalories(item.name);
  
  var controlHtml = '';
  if (qty === 0) {
    controlHtml = 
      '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,1)" ' +
      'class="px-4 py-2 bg-brandRed hover:bg-brandOrange text-white border border-brandRed rounded-xl text-xs font-black uppercase tracking-wider transition-all duration-200 active:scale-95 shadow-sm font-jakarta">' +
      '+ Add' +
      '</button>';
  } else {
    controlHtml = 
      '<div class="flex items-center rounded-xl px-2.5 py-1.5 gap-3 shrink-0 bg-brandRed text-white shadow-md shadow-brandRed/20">' +
        '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,-1)" class="w-5 h-5 flex items-center justify-center font-black active:scale-90 transition-transform text-white/80 hover:text-white">-</button>' +
        '<span class="text-xs font-black product-qty-val text-white" data-cat="' + catId + '" data-idx="' + idx + '">' + qty + '</span>' +
        '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,1)" class="w-5 h-5 flex items-center justify-center font-black active:scale-90 transition-transform text-white/80 hover:text-white">+</button>' +
      '</div>';
  }

  return (
    '<div class="bg-white rounded-3xl p-5 product-card flex flex-col justify-between gap-4 border border-gray-100/50 shadow-sm relative overflow-hidden">' +
      '<div class="space-y-3">' +
        '<!-- Top Meta Row -->' +
        '<div class="flex items-center justify-end">' +
          '<span class="bg-gray-50 px-2 py-1 rounded-lg border border-gray-100/80 shadow-2xs flex items-center justify-center shrink-0">' +
            '<span class="food-type-icon ' + (isVeg ? 'veg' : 'non-veg') + ' !mr-0"></span>' +
          '</span>' +
        '</div>' +
        '<!-- Card Content -->' +
        '<div class="space-y-1">' +
          '<h3 class="text-sm font-bold text-gray-900 leading-snug item-name-caps line-clamp-2" title="' + esc(item.name) + '">' + esc(item.name) + '</h3>' +
        '</div>' +
      '</div>' +
      '<!-- Price & Add Action Row -->' +
      '<div class="flex items-center justify-between pt-3 border-t border-gray-100/60 mt-auto">' +
        '<span class="text-base font-black text-gray-900">' + currency + item.price + '</span>' +
        '<div id="qty-pill-' + catId + '-' + idx + '">' +
          controlHtml +
        '</div>' +
      '</div>' +
    '</div>'
  );
}

function updatePillStyle(catId, idx, qty) {
  var el = document.getElementById('qty-pill-' + catId + '-' + idx);
  if (!el) return;
  
  if (qty === 0) {
    el.innerHTML = 
      '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,1)" ' +
      'class="px-4 py-2 bg-brandRed hover:bg-brandOrange text-white border border-brandRed rounded-xl text-xs font-black uppercase tracking-wider transition-all duration-200 active:scale-95 shadow-sm font-jakarta">' +
      '+ Add' +
      '</button>';
  } else {
    el.innerHTML = 
      '<div class="flex items-center rounded-xl px-2.5 py-1.5 gap-3 shrink-0 bg-brandRed text-white shadow-md shadow-brandRed/20">' +
        '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,-1)" class="w-5 h-5 flex items-center justify-center font-black active:scale-90 transition-transform text-white/80 hover:text-white">-</button>' +
        '<span class="text-xs font-black product-qty-val text-white" data-cat="' + catId + '" data-idx="' + idx + '">' + qty + '</span>' +
        '<button data-cat="' + catId + '" data-idx="' + idx + '" onclick="changeProductQty(event,1)" class="w-5 h-5 flex items-center justify-center font-black active:scale-90 transition-transform text-white/80 hover:text-white">+</button>' +
      '</div>';
  }
}

function changeProductQty(e, delta) {
  e.stopPropagation();
  var btn = e.currentTarget;
  var catId = btn.dataset.cat;
  var idx = parseInt(btn.dataset.idx);
  var cat = null;
  for (var i = 0; i < MENU_DATA.length; i++) {
    if (MENU_DATA[i].id === catId) {
      cat = MENU_DATA[i];
      break;
    }
  }
  if (!cat) {
    return;
  }
  var item = cat.items[idx];
  if (!item) {
    return;
  }

  var span = document.querySelector('.product-qty-val[data-cat="' + catId + '"][data-idx="' + idx + '"]');
  var cur = 0;
  if (span) {
    cur = parseInt(span.textContent);
  } else {
    var key = 'p:' + catId + ':' + idx;
    if (cart[key]) {
      cur = cart[key].qty;
    }
  }
  if (isNaN(cur)) {
    cur = 0;
  }
  var next = cur + delta;
  if (next < 0) {
    next = 0;
  }

  setCartItem('p:' + catId + ':' + idx, item.name, item.price, next);
  updatePillStyle(catId, idx, next);
}

function setCartItem(id, name, price, qty) {
  if (qty <= 0) {
    delete cart[id];
  } else {
    cart[id] = { name: name, price: price, qty: qty };
  }
  try {
    localStorage.setItem('guest_cart', JSON.stringify(cart));
  } catch(e) {
    console.log('failed to save cart', e);
  }
  updateCartBadge();
  var overlay = document.getElementById('cart-overlay');
  if (!overlay.classList.contains('hidden')) {
    renderCartItems();
  }
}

function updateCartBadge() {
  var total = 0;
  for (var key in cart) {
    total = total + cart[key].qty;
  }
  var counter = document.getElementById('cart-counter');
  counter.textContent = total;
  if (total === 0) {
    counter.classList.add('hidden');
  } else {
    counter.classList.remove('hidden');
  }
}

function renderCartItems() {
  var list = document.getElementById('cart-items-list');
  var totalEl = document.getElementById('cart-total');
  var keys = Object.keys(cart);
  var currency = CONFIG.cafe ? CONFIG.cafe.currency_symbol : '₹';

  if (keys.length === 0) {
    list.innerHTML = '<p class="text-center text-sm text-gray-400 py-10">Your cart is empty.</p>';
    totalEl.textContent = currency + '0';
    return;
  }

  var total = 0;
  var html = '';
  for (var i = 0; i < keys.length; i++) {
    var item = cart[keys[i]];
    total = total + (item.price * item.qty);
    html +=
      '<div class="flex items-center justify-between gap-3 bg-bgLight rounded-2xl px-4 py-3">' +
        '<div class="flex-1">' +
          '<p class="text-sm font-bold text-gray-900">' + esc(item.name) + '</p>' +
          '<p class="text-xs text-gray-500">' + currency + item.price + ' × ' + item.qty + '</p>' +
        '</div>' +
        '<span class="text-sm font-bold text-gray-900">' + currency + (item.price * item.qty) + '</span>' +
      '</div>';
  }
  list.innerHTML = html;
  totalEl.textContent = currency + total;
}

function toggleCartOverlay() {
  var overlay = document.getElementById('cart-overlay');
  var isHidden = overlay.classList.contains('hidden');
  if (isHidden) {
    document.getElementById('cart-table-label').textContent = 'Table ' + TABLE_ID;
    renderCartItems();
    overlay.classList.remove('hidden');
    setTimeout(function () {
      overlay.classList.remove('opacity-0');
    }, 10);
  } else {
    overlay.classList.add('opacity-0');
    setTimeout(function () {
      overlay.classList.add('hidden');
    }, 300);
  }
}

function placeOrder() {
  var keys = Object.keys(cart);
  if (keys.length === 0) {
    showToast('Your cart is empty');
    return;
  }
  if (typeof CONFIG === 'undefined' || !CONFIG.API_URL) {
    showToast('config.js missing');
    return;
  }

  var btn = document.getElementById('order-btn');
  btn.disabled = true;
  btn.textContent = 'Placing...';

  var orderItems = [];
  for (var i = 0; i < keys.length; i++) {
    var it = cart[keys[i]];
    orderItems.push({ name: it.name, price: it.price, qty: it.qty });
  }

  fetch(CONFIG.API_URL + '/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
    body: JSON.stringify({
      order_id: genId(),
      table_id: TABLE_ID,
      sig: ORDER_SIG,
      customer_phone: null,
      status: 'OPEN',
      items: orderItems
    })
  })
    .then(function (r) {
      if (!r.ok) {
        return r.json().then(function (e) {
          throw new Error(e.detail || ('Error ' + r.status));
        });
      }
      return r.json();
    })
    .then(function () {
      for (var k in cart) {
        delete cart[k];
      }
      try {
        localStorage.removeItem('guest_cart');
      } catch(e) {
        console.log('failed to clear cart', e);
      }
      updateCartBadge();
      renderCartItems();
      renderBakeryProducts();
      var overlay = document.getElementById('cart-overlay');
      overlay.classList.add('opacity-0');
      overlay.classList.add('hidden');
      showToast('Order placed! ✅');
      setTimeout(function () {
        window.location.replace('../index.html' + window.location.search);
      }, 1500);
    })
    .catch(function (err) {
      showToast(err.message || 'Order failed, try again');
    })
    .finally(function () {
      btn.disabled = false;
      btn.textContent = 'PLACE TABLE ORDER';
    });
}

function backToMenu(e) {
  if (e) e.preventDefault();
  window.location.href = 'menu.html' + window.location.search;
}

function goHome(e) {
  if (e) e.preventDefault();
  window.location.replace('../index.html' + window.location.search);
}

function esc(str) {
  var d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function genId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return 'ord_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
}

function showToast(msg) {
  var t = document.getElementById('order-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'order-toast';
    t.className = 'fixed bottom-24 left-1/2 -translate-x-1/2 z-[60] bg-gray-900 text-white text-sm font-medium px-5 py-3 rounded-full shadow-lg whitespace-nowrap max-w-[85vw] pointer-events-none transition-all duration-300 opacity-0 translate-y-4';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  clearTimeout(t._t);
  setTimeout(function () {
    t.classList.remove('opacity-0', 'translate-y-4');
  }, 10);
  t._t = setTimeout(function () {
    t.classList.add('opacity-0', 'translate-y-4');
  }, 2500);
}
