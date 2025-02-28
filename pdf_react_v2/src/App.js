import React, { useState, useRef, useEffect } from "react";
import * as pdfjsLib from "pdfjs-dist/build/pdf";
import "pdfjs-dist/build/pdf.worker.entry";

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js`;

const PDFSelector = () => {
  const [pdf, setPdf] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [rects, setRects] = useState([]);
  const [currentRect, setCurrentRect] = useState(null);
  const pdfCanvasRef = useRef(null);
  const containerRef = useRef(null);
  const renderTaskRef = useRef(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const loadPdf = async () => {
      try {
        const loadingTask = pdfjsLib.getDocument("/FACTURA_AVON.PDF");
        const pdfDoc = await loadingTask.promise;
        setPdf(pdfDoc);
        renderPage(pdfDoc, pageNumber);
      } catch (error) {
        console.error("Error al cargar el PDF:", error);
      }
    };
    loadPdf();
  }, []);

  useEffect(() => {
    if (pdf) {
      renderPage(pdf, pageNumber);
    }
  }, [pdf, pageNumber]);

  const renderPage = async (pdfDoc, pageNum) => {
    const page = await pdfDoc.getPage(pageNum);
    const container = containerRef.current;
    const viewport = page.getViewport({ scale: 1 });

    const scaleFactor = Math.min(
      container.clientWidth / viewport.width,
      container.clientHeight / viewport.height
    );
    setScale(scaleFactor);

    const scaledViewport = page.getViewport({ scale: scaleFactor });
    const canvas = pdfCanvasRef.current;
    const context = canvas.getContext("2d");

    if (renderTaskRef.current) {
      renderTaskRef.current.cancel();
    }

    canvas.width = scaledViewport.width;
    canvas.height = scaledViewport.height;

    const renderContext = { canvasContext: context, viewport: scaledViewport };
    renderTaskRef.current = page.render(renderContext);

    try {
      await renderTaskRef.current.promise;
    } catch (error) {
      if (error.name !== "RenderingCancelledException") {
        console.error("Error al renderizar la página:", error);
      }
    }
  };

  const handleMouseDown = (e) => {
    e.preventDefault();
    const { left, top } = pdfCanvasRef.current.getBoundingClientRect();
    const startX = (e.clientX - left) / scale;
    const startY = (e.clientY - top) / scale;

    setCurrentRect({ startX, startY, endX: startX, endY: startY });

    const handleMouseMove = (e) => {
      const endX = (e.clientX - left) / scale;
      const endY = (e.clientY - top) / scale;

      setCurrentRect((prev) => ({
        ...prev,
        endX,
        endY,
      }));
    };

    const handleMouseUp = () => {
      if (currentRect) {
        setRects((prevRects) => [...prevRects, { ...currentRect }]);
      }
      setCurrentRect(null);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div ref={containerRef} style={{ position: "relative", overflow: "auto", height: "80vh", width: "80vw" }}>
        <canvas ref={pdfCanvasRef} style={{ display: "block" }} onMouseDown={handleMouseDown}></canvas>
        {rects.map((rect, index) => (
          <div
            key={index}
            style={{
              position: "absolute",
              border: "2px dashed red",
              left: rect.startX * scale,
              top: rect.startY * scale,
              width: (rect.endX - rect.startX) * scale,
              height: (rect.endY - rect.startY) * scale,
              backgroundColor: "rgba(255, 0, 0, 0.2)",
              pointerEvents: "none"
            }}
          />
        ))}

        {currentRect && (
          <div
            style={{
              position: "absolute",
              border: "2px dashed blue",
              left: currentRect.startX * scale,
              top: currentRect.startY * scale,
              width: (currentRect.endX - currentRect.startX) * scale,
              height: (currentRect.endY - currentRect.startY) * scale,
              backgroundColor: "rgba(0, 0, 255, 0.2)",
              pointerEvents: "none"
            }}
          />
        )}
      </div>
      <button onClick={() => setPageNumber(pageNumber - 1)} disabled={pageNumber === 1}>Página Anterior</button>
      <button onClick={() => setPageNumber(pageNumber + 1)} disabled={!pdf || pageNumber >= pdf.numPages}>Página Siguiente</button>
      <div>
        <h3>Coordenadas Extraídas</h3>
        <ul>
          {rects.map((rect, index) => (
            <li key={index}>
              Rect {index + 1}: [{rect.startY.toFixed(2)}, {rect.startX.toFixed(2)}, {rect.endY.toFixed(2)}, {rect.endX.toFixed(2)}]
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default PDFSelector;
