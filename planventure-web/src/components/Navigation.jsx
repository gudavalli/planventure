
import { Link } from 'react-router-dom';
import { useAuth } from '../context/auth-hooks';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Users', href: '/users', adminOnly: true },
  { name: 'Assessments', href: '/assessments', roles: ['admin', 'talent_lead'] },
];

const Navigation = () => {
  const { user, logout } = useAuth();  const handleLogout = (e) => {
    e.preventDefault();
    logout();
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container-fluid">
        <Link className="navbar-brand" to={user?.role === 'admin' ? '/users' : '/dashboard'}>PlanVenture</Link>
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav" 
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {navigation.map((item) => {
              // Check if the item should be displayed based on role
              let showItem = true;
              
              // Admin-only items
              if (item.adminOnly && (!user || user.role !== 'admin')) {
                showItem = false;
              }
              
              // Role-specific items
              if (item.roles && (!user || !item.roles.includes(user.role))) {
                showItem = false;
              }
              
              return showItem && (
                <li className="nav-item" key={item.name}>
                  <Link 
                    className="nav-link" 
                    to={item.href}
                  >
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
          <div className="dropdown">
            <button 
              className="btn btn-outline-secondary dropdown-toggle"
              type="button"
              id="userDropdown"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i className="bi bi-person-circle"></i> Account
            </button>
            <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
              <li>
                <Link className="dropdown-item" to="/profile">Your Profile</Link>
              </li>
              <li><hr className="dropdown-divider" /></li>
              <li>
                <button className="dropdown-item" onClick={handleLogout}>Sign out</button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
