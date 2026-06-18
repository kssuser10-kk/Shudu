import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="数独游戏",
    page_icon="🧩",
    layout="centered"
)

html_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
        background: #ffffff;
        color: #222;
        margin: 0;
        padding: 0;
    }

    .wrap {
        width: 100%;
        max-width: 620px;
        margin: 0 auto;
        padding: 10px 0 30px;
        text-align: center;
    }

    h1 {
        margin: 8px 0 4px;
        font-size: 32px;
        font-weight: 800;
    }

    .rule {
        color: #666;
        font-size: 14px;
        margin-bottom: 16px;
    }

    .topbar {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 14px;
    }

    select, button {
        height: 36px;
        border-radius: 8px;
        border: 1px solid #d0d0d0;
        background: white;
        padding: 0 12px;
        font-size: 14px;
        cursor: pointer;
    }

    button:hover {
        background: #f3f3f3;
    }

    .info {
        margin: 8px 0 14px;
        font-size: 14px;
        color: #555;
    }

    .board {
        display: grid;
        grid-template-columns: repeat(9, 52px);
        grid-template-rows: repeat(9, 52px);
        justify-content: center;
        margin: 0 auto;
        width: fit-content;
        background: #111;
        border: 3px solid #111;
    }

    .cell {
        width: 52px;
        height: 52px;
        box-sizing: border-box;
        border: 1px solid #999;
        text-align: center;
        font-size: 25px;
        font-weight: 700;
        color: #222;
        background: #ffffff;
        outline: none;
        caret-color: #222;
    }

    .cell:focus {
        background: #eef5ff;
        box-shadow: inset 0 0 0 2px #2b7cff;
    }

    .given {
        background: #e9ecef;
        color: #555;
        font-weight: 800;
    }

    .duplicate {
        background: #fff3df !important;
        box-shadow: inset 0 0 0 3px #ff9800 !important;
    }

    .wrong {
        background: #ffe8e8 !important;
        box-shadow: inset 0 0 0 3px #e53935 !important;
    }

    .bt {
        border-top: 3px solid #111 !important;
    }

    .bl {
        border-left: 3px solid #111 !important;
    }

    .br {
        border-right: 3px solid #111 !important;
    }

    .bb {
        border-bottom: 3px solid #111 !important;
    }

    .message {
        min-height: 28px;
        margin-top: 14px;
        font-size: 15px;
        font-weight: 600;
    }

    .ok {
        color: #16833a;
    }

    .warn {
        color: #d97900;
    }

    .bad {
        color: #d32f2f;
    }

    @media (max-width: 560px) {
        .board {
            grid-template-columns: repeat(9, 38px);
            grid-template-rows: repeat(9, 38px);
        }

        .cell {
            width: 38px;
            height: 38px;
            font-size: 20px;
        }

        h1 {
            font-size: 26px;
        }
    }
</style>
</head>

<body>
<div class="wrap">
    <h1>数独游戏</h1>
    <div class="rule">规则：每行、每列、每个 3×3 宫内填入 1–9，且不能重复。</div>

    <div class="topbar">
        <select id="difficulty">
            <option value="easy">简单</option>
            <option value="medium" selected>中等</option>
            <option value="hard">困难</option>
            <option value="expert">专家</option>
        </select>

        <button onclick="newGame()">新游戏</button>
        <button onclick="checkAnswer()">检查答案</button>
        <button onclick="giveHint()">提示</button>
        <button onclick="clearBoard()">清空</button>
        <button onclick="showSolution()">显示答案</button>
    </div>

    <div class="info">
        用时：<span id="timer">00:00</span>
        ｜提示次数：<span id="hintCount">0</span>
    </div>

    <div class="board" id="board"></div>

    <div class="message" id="message"></div>
</div>

<script>
const basePuzzles = {
    easy: {
        puzzle: [
            "530070000",
            "600195000",
            "098000060",
            "800060003",
            "400803001",
            "700020006",
            "060000280",
            "000419005",
            "000080079"
        ],
        solution: [
            "534678912",
            "672195348",
            "198342567",
            "859761423",
            "426853791",
            "713924856",
            "961537284",
            "287419635",
            "345286179"
        ]
    },
    medium: {
        puzzle: [
            "000134000",
            "005692401",
            "300000006",
            "250900100",
            "000005600",
            "060080507",
            "070400050",
            "104853702",
            "030267000"
        ],
        solution: [
            "726134895",
            "985692431",
            "341578926",
            "253946178",
            "417325689",
            "869781547",
            "672419358",
            "194853762",
            "538267914"
        ]
    },
    hard: {
        puzzle: [
            "000000010",
            "400000000",
            "020000000",
            "000050407",
            "008000300",
            "001090000",
            "300400200",
            "050100000",
            "000806000"
        ],
        solution: [
            "693784512",
            "487512936",
            "125963874",
            "932651487",
            "568247391",
            "741398625",
            "319475268",
            "856129743",
            "274836159"
        ]
    },
    expert: {
        puzzle: [
            "100007090",
            "030020008",
            "009600500",
            "005300900",
            "010080002",
            "600004000",
            "300000010",
            "040000007",
            "007000300"
        ],
        solution: [
            "162857493",
            "534129678",
            "789643521",
            "475312986",
            "913586742",
            "628794135",
            "356478219",
            "241935867",
            "897261354"
        ]
    }
};

let puzzle = [];
let solution = [];
let hintCount = 0;
let startTime = Date.now();
let timerInterval = null;

function strRowsToGrid(rows) {
    return rows.map(row => row.split("").map(x => Number(x)));
}

function randomDigitMap() {
    let nums = [1,2,3,4,5,6,7,8,9];
    for (let i = nums.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [nums[i], nums[j]] = [nums[j], nums[i]];
    }

    let map = {};
    for (let i = 1; i <= 9; i++) {
        map[i] = nums[i - 1];
    }
    map[0] = 0;
    return map;
}

function remapGrid(grid, map) {
    return grid.map(row => row.map(v => map[v]));
}

function newGame() {
    const difficulty = document.getElementById("difficulty").value;
    const data = basePuzzles[difficulty];

    const map = randomDigitMap();

    puzzle = remapGrid(strRowsToGrid(data.puzzle), map);
    solution = remapGrid(strRowsToGrid(data.solution), map);

    hintCount = 0;
    document.getElementById("hintCount").innerText = hintCount;
    document.getElementById("message").innerText = "";
    document.getElementById("message").className = "message";

    startTime = Date.now();

    renderBoard();
    startTimer();
}

function renderBoard() {
    const board = document.getElementById("board");
    board.innerHTML = "";

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const input = document.createElement("input");
            input.classList.add("cell");

            if (r % 3 === 0) input.classList.add("bt");
            if (c % 3 === 0) input.classList.add("bl");
            if (c === 8) input.classList.add("br");
            if (r === 8) input.classList.add("bb");

            input.dataset.row = r;
            input.dataset.col = c;
            input.maxLength = 1;
            input.inputMode = "numeric";

            if (puzzle[r][c] !== 0) {
                input.value = puzzle[r][c];
                input.disabled = true;
                input.classList.add("given");
            } else {
                input.value = "";
                input.addEventListener("input", function() {
                    this.value = this.value.replace(/[^1-9]/g, "");
                    updateDuplicateHighlight();
                });
            }

            board.appendChild(input);
        }
    }

    updateDuplicateHighlight();
}

function getCells() {
    return Array.from(document.querySelectorAll(".cell"));
}

function getGrid() {
    let grid = Array.from({ length: 9 }, () => Array(9).fill(0));

    getCells().forEach(cell => {
        const r = Number(cell.dataset.row);
        const c = Number(cell.dataset.col);
        const v = Number(cell.value);
        grid[r][c] = Number.isInteger(v) && v >= 1 && v <= 9 ? v : 0;
    });

    return grid;
}

function markDuplicatesInUnit(cells, duplicateSet) {
    let seen = {};

    cells.forEach(([r, c]) => {
        const grid = getGrid();
        const v = grid[r][c];

        if (v >= 1 && v <= 9) {
            if (!seen[v]) seen[v] = [];
            seen[v].push([r, c]);
        }
    });

    Object.values(seen).forEach(positions => {
        if (positions.length > 1) {
            positions.forEach(([r, c]) => {
                duplicateSet.add(`${r}-${c}`);
            });
        }
    });
}

function updateDuplicateHighlight() {
    const duplicateSet = new Set();

    for (let r = 0; r < 9; r++) {
        markDuplicatesInUnit(
            Array.from({ length: 9 }, (_, c) => [r, c]),
            duplicateSet
        );
    }

    for (let c = 0; c < 9; c++) {
        markDuplicatesInUnit(
            Array.from({ length: 9 }, (_, r) => [r, c]),
            duplicateSet
        );
    }

    for (let br = 0; br < 9; br += 3) {
        for (let bc = 0; bc < 9; bc += 3) {
            let cells = [];
            for (let r = br; r < br + 3; r++) {
                for (let c = bc; c < bc + 3; c++) {
                    cells.push([r, c]);
                }
            }
            markDuplicatesInUnit(cells, duplicateSet);
        }
    }

    getCells().forEach(cell => {
        const key = `${cell.dataset.row}-${cell.dataset.col}`;
        cell.classList.remove("duplicate");
        cell.classList.remove("wrong");

        if (duplicateSet.has(key)) {
            cell.classList.add("duplicate");
        }
    });
}

function checkAnswer() {
    updateDuplicateHighlight();

    const grid = getGrid();
    const cells = getCells();
    const message = document.getElementById("message");

    let empty = 0;
    let wrong = 0;
    let duplicate = document.querySelectorAll(".duplicate").length;

    cells.forEach(cell => cell.classList.remove("wrong"));

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            if (grid[r][c] === 0) {
                empty++;
            } else if (grid[r][c] !== solution[r][c]) {
                wrong++;
                const cell = document.querySelector(`[data-row="${r}"][data-col="${c}"]`);
                if (cell && !cell.disabled) {
                    cell.classList.add("wrong");
                }
            }
        }
    }

    if (duplicate > 0) {
        message.innerText = "存在重复数字，橙色格子需要修改。";
        message.className = "message warn";
        return;
    }

    if (wrong > 0) {
        message.innerText = `有 ${wrong} 个格子不正确，红色格子需要修改。`;
        message.className = "message bad";
        return;
    }

    if (empty > 0) {
        message.innerText = `目前没有发现错误，还剩 ${empty} 个空格。`;
        message.className = "message warn";
        return;
    }

    message.innerText = "完成。答案正确。";
    message.className = "message ok";
}

function giveHint() {
    let emptyCells = [];

    getCells().forEach(cell => {
        if (!cell.disabled && cell.value === "") {
            emptyCells.push(cell);
        }
    });

    if (emptyCells.length === 0) {
        return;
    }

    const cell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
    const r = Number(cell.dataset.row);
    const c = Number(cell.dataset.col);

    cell.value = solution[r][c];
    hintCount++;
    document.getElementById("hintCount").innerText = hintCount;

    updateDuplicateHighlight();
}

function clearBoard() {
    getCells().forEach(cell => {
        if (!cell.disabled) {
            cell.value = "";
            cell.classList.remove("duplicate");
            cell.classList.remove("wrong");
        }
    });

    document.getElementById("message").innerText = "";
    document.getElementById("message").className = "message";
}

function showSolution() {
    getCells().forEach(cell => {
        const r = Number(cell.dataset.row);
        const c = Number(cell.dataset.col);
        cell.value = solution[r][c];
        cell.classList.remove("duplicate");
        cell.classList.remove("wrong");
    });

    document.getElementById("message").innerText = "已显示答案。";
    document.getElementById("message").className = "message ok";
}

function startTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
    }

    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
        const s = String(elapsed % 60).padStart(2, "0");
        document.getElementById("timer").innerText = `${m}:${s}`;
    }, 1000);
}

newGame();
</script>
</body>
</html>
"""

components.html(html_code, height=760, scrolling=False)
