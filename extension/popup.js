// Та же логика, что в питоне (gospel.py): режем текст на слова,
// ищем начала слов из таблицы, считаем грехи, показываем шкалу и стих.
// Слова и стихи (WORDS и VERSES) лежат в data.js — его создаёт питон.

// Текст для проверки, если popup.html открыт просто как страница, а не как расширение
const DEMO = {
  site: "demo.local",
  text: "Распродажа! Купи лучший премиум-бургер со скидкой, закажи пиццу и десерт. Кэшбэк и бонусы. Скандал: блогер ненавидит хейтеров.",
};

// ---------- 1. Берём текст открытой страницы ----------

async function getPage() {
  if (!globalThis.chrome?.scripting) return DEMO;
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const [result] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.body.innerText, // этот кусок выполняется на самой странице
  });
  return { site: new URL(tab.url).hostname, text: result.result };
}

// ---------- 2. Считаем грехи (как count_sins в питоне) ----------

function countSins(text) {
  const counts = {};
  const words = text.toLowerCase().match(/[\p{L}\p{N}_]+/gu) || [];
  for (const word of words) {
    for (const [sin, stems] of Object.entries(WORDS)) {
      if (stems.some((stem) => word.startsWith(stem))) {
        counts[sin] = (counts[sin] || 0) + 1;
      }
    }
  }
  return counts;
}

function randomItem(list) {
  return list[Math.floor(Math.random() * list.length)];
}

// 1 грех, 2 греха, 5 грехов
function sinWord(n) {
  if (n % 10 === 1 && n % 100 !== 11) return "грех";
  if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return "греха";
  return "грехов";
}

// ---------- 3. Рисуем шкалу ----------

function showBars(counts) {
  const bars = document.getElementById("bars");
  const sins = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
  if (sins.length === 0) {
    bars.innerHTML = '<p class="muted">грехов не найдено</p>';
    return;
  }
  const biggest = counts[sins[0]];
  for (const sin of sins) {
    const width = Math.max(4, Math.round((counts[sin] / biggest) * 100));
    bars.insertAdjacentHTML(
      "beforeend",
      `<div class="row">
        <div class="row-head"><span>${sin.toLowerCase()}</span><span>${counts[sin]}</span></div>
        <div class="track"><div class="fill" style="width: ${width}%"></div></div>
      </div>`,
    );
  }
}

// ---------- 4. Показываем стих ----------

// Стих встаёт сразу под шкалой, сколько бы в ней ни было строк
function placeVerse() {
  const scale = document.querySelector(".scale");
  document.getElementById("verse-block").style.top = `${scale.offsetTop + scale.offsetHeight + 24}px`;
}

// "«Текст» (Мф 6:24)" → текст и ссылка отдельно
function showVerse(line) {
  const [, text, ref] = line.match(/^(.*) \((.+)\)$/);
  document.getElementById("verse").textContent = text;
  document.getElementById("ref").textContent = ref;
  // стих каждый раз заново выплывает снизу наискосок
  const block = document.getElementById("verse-block");
  block.classList.remove("enter");
  void block.offsetWidth; // перезапуск анимации
  block.classList.add("enter");
}

// ---------- 5. Глитч: экран плывёт и ложится стопкой копий ----------

function glitch(swap) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    swap();
    return;
  }

  const screen = document.getElementById("screen");
  const turbulence = document.getElementById("turbulence");
  const displace = document.getElementById("displace");

  // Копии экрана, которые съезжают вниз и сплющиваются
  const copies = [];
  for (let i = 1; i <= 6; i++) {
    const copy = screen.cloneNode(true);
    copy.removeAttribute("id");
    copy.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
    copy.className = "echo";
    copy.style.filter = "url(#wave)";
    document.body.append(copy);
    copies.push(copy);
  }
  screen.style.filter = "url(#wave)";

  const duration = 900;
  const start = performance.now();
  let swapped = false;

  function frame(now) {
    const progress = Math.min(1, (now - start) / duration);
    const power = Math.sin(progress * Math.PI); // 0 → 1 → 0

    displace.setAttribute("scale", 70 * power);
    turbulence.setAttribute("seed", Math.floor(now / 70)); // волна всё время меняется

    copies.forEach((copy, i) => {
      const k = i + 1;
      copy.style.transform = `translateY(${k * 14 * power}px) scaleY(${1 - k * 0.1 * power})`;
      copy.style.opacity = 0.6 * power * (1 - i / copies.length);
    });

    if (!swapped && progress > 0.5) {
      swap();
      swapped = true;
    }

    if (progress < 1) {
      requestAnimationFrame(frame);
    } else {
      copies.forEach((copy) => copy.remove());
      screen.style.filter = "";
      displace.setAttribute("scale", 0);
    }
  }

  requestAnimationFrame(frame);
}

// ---------- 6. Собираем всё вместе ----------

async function main() {
  let page;
  try {
    page = await getPage();
  } catch {
    document.getElementById("site").textContent = "нет доступа к этой странице";
    showVerse(randomItem(VERSES["Чистая страница"]));
    return;
  }

  const counts = countSins(page.text);
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const sins = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
  const topSin = sins[0] || "Чистая страница";

  document.getElementById("site").textContent = page.site;
  document.getElementById("total").textContent = total;
  document.getElementById("total-word").textContent = sinWord(total);
  showBars(counts);
  placeVerse();
  showVerse(randomItem(VERSES[topSin]));

  document.getElementById("next").addEventListener("click", () => {
    glitch(() => showVerse(randomItem(VERSES[topSin])));
  });
}

main();
