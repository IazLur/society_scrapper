import { useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'

const API = window.CONFIG?.API_URL || 'http://127.0.0.1:5000'

function Login({onLogin, switchToRegister}){
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [error,setError]=useState('');
  const submit=async(e)=>{
    e.preventDefault();
    setError('');
    const r=await fetch(`${API}/api/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
    if(r.ok){
      const data=await r.json();
      onLogin(data.token,data.username);
    }else{
      setError('Login failed');
    }
  }
  return (
    <div className="container mt-5" style={{maxWidth:'400px'}}>
      <h2>Login</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={submit}>
        <div className="mb-3">
          <label className="form-label">Email</label>
          <input className="form-control" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label">Password</label>
          <input type="password" className="form-control" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary">Login</button>
        <button type="button" className="btn btn-link" onClick={switchToRegister}>Register</button>
      </form>
    </div>
  );
}

function Register({onRegister, switchToLogin}){
  const [username,setUsername]=useState('');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [error,setError]=useState('');
  const submit=async(e)=>{
    e.preventDefault();
    setError('');
    const r=await fetch(`${API}/api/register`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,email,password})});
    if(r.ok){
      onRegister();
    }else{
      setError('Registration failed');
    }
  }
  return (
    <div className="container mt-5" style={{maxWidth:'400px'}}>
      <h2>Register</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={submit}>
        <div className="mb-3">
          <label className="form-label">Username</label>
          <input className="form-control" value={username} onChange={e=>setUsername(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label">Email</label>
          <input className="form-control" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label">Password</label>
          <input type="password" className="form-control" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary">Register</button>
        <button type="button" className="btn btn-link" onClick={switchToLogin}>Back to login</button>
      </form>
    </div>
  );
}

function Search({token,username}){
  const [domain,setDomain]=useState('');
  const [results,setResults]=useState([]);
  const [name,setName]=useState('');
  const search=async(e)=>{
    e.preventDefault();
    const params=new URLSearchParams({domain});
    const r=await fetch(`${API}/api/search?`+params.toString(),{headers:{'Authorization':'Bearer '+token}});
    if(r.ok){
      const data=await r.json();
      setResults(data.results);
      setName(data.name);
    }
  }
  return (
    <div className="container mt-5">
      <h2>Welcome {username}</h2>
      <form onSubmit={search} className="mb-3">
        <div className="input-group">
          <input className="form-control" placeholder="Domain" value={domain} onChange={e=>setDomain(e.target.value)} />
          <button className="btn btn-success">Search</button>
        </div>
      </form>
      {name && <h4>Results for {name}</h4>}
      <ul className="list-group">
        {results.map(c=>(
          <li key={c.siren} className="list-group-item">
            <strong>{c.nom_raison_sociale}</strong> - SIREN {c.siren} - Score {c.score.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}

function App(){
  const [token,setToken]=useState(null);
  const [username,setUsername]=useState('');
  const [page,setPage]=useState('login');
  if(!token){
    if(page==='login') return <Login onLogin={(t,u)=>{setToken(t);setUsername(u);}} switchToRegister={()=>setPage('register')} />
    return <Register onRegister={()=>setPage('login')} switchToLogin={()=>setPage('login')} />
  }
  return <Search token={token} username={username} />
}

export default App
