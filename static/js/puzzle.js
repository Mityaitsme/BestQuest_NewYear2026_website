document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('puzzle-board');
    if (!board) return;

    // 1. Твоя СТАРТОВАЯ расстановка
    // null - это пустая клетка (дырка)
    // Ряд 3: "14 13 12 null" -> значит null на 4-й позиции в 3 ряду
    let state = [
        1, 2, 4, 8,     // 1 ряд
        6, 7, 10, 3,    // 2 ряд
        15, 14, 12, null, // 3 ряд (индекс 11 - пустой)
        5, 11, 9, 16    // 4 ряд
    ];
    /*let state = [
        1, 2, 3, 4,     // 1 ряд
        5, 6, 7, 8,
        9, 10, 11, 12,
        14, null, 15, 16
    ];*/

    // 2. ПОБЕДНАЯ расстановка (Дырка в левом нижнем углу - индекс 12)
    // Логичный порядок: 1..12, потом Дырка, потом 13..15
    const winState = [
        1, 2, 3, 4,
        5, 6, 7, 8,
        9, 10, 11, 12,
        null, 14, 15, 16
    ];

    function render() {
        board.innerHTML = '';
        state.forEach((num, index) => {
            const tile = document.createElement('div');
            // Если num === null, добавляем класс empty
            tile.className = 'tile' + (num === null ? ' empty' : '');
            
            if (num !== null) {
                // Если ты используешь картинки (раскомментируй в CSS), то код ниже нужен для них:
                
                tile.style.backgroundImage = `url('/static/img/puzzle/${num}.png')`;
                tile.style.backgroundSize = '100% 100%';
                tile.innerText = ''; 
                
               
                // Если пока используешь цифры:
                /* tile.innerText = num;*/
            }
            
            tile.onclick = () => move(index);
            board.appendChild(tile);
        });
        
        // Проверяем победу после отрисовки
        // Небольшая задержка, чтобы успел отрисоваться последний ход
        setTimeout(checkWin, 100);
    }

    function move(index) {
        const emptyIndex = state.indexOf(null);
        const validMoves = [index - 1, index + 1, index - 4, index + 4];

        if (validMoves.includes(emptyIndex)) {
            // Проверка, чтобы не перепрыгивать через границы строк
            const row = Math.floor(index / 4);
            const emptyRow = Math.floor(emptyIndex / 4);
            // Если разница в рядах больше 1 (или 0 при ходе вбок, но мы проверяем row shift),
            // для лево-право: они должны быть в одном ряду
            if (Math.abs(index - emptyIndex) === 1 && row !== emptyRow) return;

            // Меняем местами
            state[emptyIndex] = state[index];
            state[index] = null;
            render();
        }
    }

    function checkWin() {
      const isWin = state.every((val, index) => val === winState[index]);

      if (isWin) {
          const overlay = document.getElementById('white-overlay');
          const puzzleContainer = document.getElementById('puzzle-container');
          const secretRoom = document.getElementById('secret-room');

          // ЭТАП 1: Начинаем медленно заливать белым (длится 3 секунды по CSS)
          overlay.style.opacity = '1';

          // Ждем 3 секунды (3000 мс), пока экран полностью побелеет
          setTimeout(() => {
              
              // ЭТАП 2: Пока экран белый, меняем декорации
              puzzleContainer.style.display = 'none';
              secretRoom.style.display = 'block';
              
              // ЭТАП 3: Делаем маленькую паузу (0.5 сек), чтобы насладиться белым цветом
              // И только потом начинаем проявлять комнату
              setTimeout(() => {
                  overlay.style.opacity = '0';
              }, 500);

          }, 3000); // Это время должно совпадать с transition в CSS
      }
    }

    render();
});

// Функции для модальных окон (оставляем без изменений)
function openModal(id) {
    document.getElementById(id).style.display = 'block';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}