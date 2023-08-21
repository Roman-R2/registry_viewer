'use strict'

function setOrClearActiveClass(els) {
  /**
   * Получает элементы и в зависимости от страницы сайт (pathname)
   * устанавливает класс active или убирает его
   */

  els.forEach(function(el){
    // Найдем из href ссылки страницу сайта без хоста и протокола
    let clearPage = el.href;
    clearPage = clearPage.replace(window.location.protocol + '//', '');
    clearPage = clearPage.replace(el.host, '');

    //найдем главный путь из всего пути страницы
    let mainPath = clearPage.split('/')
    // Удалим из массива все элементы ''
    mainPath = mainPath.filter(item => item !== '')

    // Добавим класс active если совпадают страницы сайта, иначе удалим класс active
    if (
      // Если pathname окна равен полученному pathname из текущей ссылки
      window.location.pathname === clearPage ||
      (
        // Или если в pathname окна содержится первый элемент пути, заключенный между '/'
        window.location.pathname.indexOf('/' + mainPath[0] + '/') > -1 &&
        // И при этом путь больше не продолжается
        typeof mainPath[1] === 'undefined'
      )
    ) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });
}

let navbarEls = document.querySelectorAll("#navbar a");

setOrClearActiveClass(navbarEls);
