import Navigation from '../components/Navigation';
import { useAuth } from '../context/auth-hooks';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <main className="container py-4">
        <div className="row">
          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body">
                <h1 className="h3 mb-3">
                  Welcome, {user?.first_name || 'User'}!
                </h1>
                
                <div className="p-5 border border-2 border-dashed rounded d-flex align-items-center justify-content-center" style={{ height: '400px' }}>
                  <p className="text-muted">
                    Dashboard content will be displayed here. This is a placeholder.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="row mt-4">
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header">
                Recent Activities
              </div>
              <div className="card-body">
                <p className="card-text">No recent activities to display.</p>
              </div>
            </div>
          </div>
          
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header">
                Upcoming Plans
              </div>
              <div className="card-body">
                <p className="card-text">No upcoming plans to display.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
