import { useRef } from 'react';
import { useReactToPrint } from 'react-to-print';
import Button from '../Button';

// This component provides PDF export functionality for assessment results
const PDFExport = ({ children, filename = 'assessment-report.pdf' }) => {
  const contentRef = useRef(null);

  const handlePrint = useReactToPrint({
    content: () => contentRef.current,
    documentTitle: filename,
    onBeforeGetContent: () => {
      // Add any pre-print preparations here
      return Promise.resolve();
    },
    onAfterPrint: () => {
      // Add any post-print actions here
    }
  });

  return (
    <div className="pdf-export">
      <Button 
        className="btn btn-outline-primary mb-4" 
        onClick={handlePrint}
      >
        <i className="bi bi-file-earmark-pdf me-2"></i>
        Export as PDF
      </Button>
      
      <div ref={contentRef} className="pdf-content">
        {children}
      </div>
    </div>
  );
};

export default PDFExport;
