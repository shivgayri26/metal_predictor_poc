import React, {useEffect, useState, useRef} from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import MultiMetalCards from './MultiMetalCards';
import ForecastTable from './ForecastTable';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';

export default function Dashboard(){
  const [data, setData] = useState([]);
  const [rawRows, setRawRows] = useState([]);
  const [price, setPrice] = useState(null);
  const [metal, setMetal] = useState('gold');
  const [loading, setLoading] = useState(true);
  const reportRef = useRef(null);

  function fetchFor(m='gold'){
    setLoading(true);
    // URL must be a quoted string; use template literal to inject metal
    axios.get(http://127.0.0.1:8000/predict?metal=&days=7, { timeout: 5000 })
      .then(res => {
        const mapped = res.data.map(r => ({date: r.date.split(' ')[0], value: Math.round(r.forecast), raw: r}));
        setData(mapped);
        setRawRows(res.data || []);
        setPrice(mapped.length ? mapped[mapped.length-1].value : null);
      })
      .catch(()=> {
        setData([]);
        setRawRows([]);
        setPrice(null);
      })
      .finally(()=> setLoading(false));
  }

  useEffect(()=> { fetchFor(metal); }, [metal]);

  function exportCSV(){
    if(!rawRows || rawRows.length===0) return;
    const header = 'date,forecast,low,high\\n';
    const rows = rawRows.map(r => ${r.date},,,).join('\\n');
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, ${metal}_forecast.csv);
  }

  async function exportPDF(){
    if (!reportRef.current) return;
    const el = reportRef.current;
    const canvas = await html2canvas(el, { scale: 2, useCORS: true });
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({ orientation: 'landscape', unit: 'pt', format: [canvas.width, canvas.height] });
    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save(${metal}_forecast_report.pdf);
  }

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='text-2xl font-semibold'>{metal.toUpperCase()} — 7 day forecast</h2>
          <p className='text-sm text-gray-400'>Latest prediction and confidence bands</p>
        </div>
        <div className='text-right'>
          <div className='text-lg text-gray-300'>Estimated</div>
          <div className='text-3xl font-bold' style={{color:'#D4AF37'}}>{loading ? '...' : price}</div>
        </div>
      </div>

      <MultiMetalCards onSelect={(m) => setMetal(m)} />

      <div ref={reportRef}>
        <div className='bg-[#071022] rounded-xl p-6 shadow mb-4'>
          <div style={{height:340}}>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart data={data}>
                <XAxis dataKey='date' stroke='#94a3b8' />
                <YAxis stroke='#94a3b8' />
                <Tooltip />
                <Line type='monotone' dataKey='value' stroke='#D4AF37' strokeWidth={2} dot={false}/>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <ForecastTable rows={rawRows} metal={metal} onExportCSV={exportCSV} onExportPDF={exportPDF} />
      </div>
    </div>
  );
}