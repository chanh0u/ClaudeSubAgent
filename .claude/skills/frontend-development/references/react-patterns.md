# React Patterns — React 패턴

React 개발에서 자주 사용하는 패턴.

## 1. 컴포넌트 구조

```jsx
// 함수형 컴포넌트
function TodoItem({ todo, onToggle, onDelete }) {
  return (
    <div>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span>{todo.title}</span>
      <button onClick={() => onDelete(todo.id)}>삭제</button>
    </div>
  );
}
```

## 2. Hooks

### useState
```jsx
const [count, setCount] = useState(0);
setCount(count + 1);
```

### useEffect
```jsx
useEffect(() => {
  // 마운트 시 실행
  fetchData();
}, []); // 빈 배열: 1회만
```

### useContext
```jsx
const ThemeContext = React.createContext();

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Child />
    </ThemeContext.Provider>
  );
}

function Child() {
  const theme = useContext(ThemeContext);
  return <div>Theme: {theme}</div>;
}
```

## 3. 조건부 렌더링

```jsx
{loading && <div>Loading...</div>}
{error && <div>Error: {error}</div>}
{data && <div>{data.name}</div>}
```

## 4. 리스트 렌더링

```jsx
{todos.map(todo => (
  <TodoItem key={todo.id} todo={todo} />
))}
```

## 참조

- API 통합: [api-integration.md](api-integration.md)
