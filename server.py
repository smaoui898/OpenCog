import json
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import sys
import os

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pln_reasoning.queries import diagnose_patient, explain_diagnosis

PORT = 8000

class MedicalDemoRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route API request
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/api/diagnose':
            self.handle_api_diagnose(parsed_url)
        else:
            # Map root path to serve demo.html automatically
            if parsed_url.path == '/' or parsed_url.path == '':
                self.path = '/demo.html'
            super().do_GET()

    def handle_api_diagnose(self, parsed_url):
        try:
            # Parse symptoms query param
            query_params = urllib.parse.parse_qs(parsed_url.query)
            symptoms_raw = query_params.get('symptoms', [''])
            
            # Split comma-separated symptoms
            symptoms = [s.strip() for s in symptoms_raw[0].split(',') if s.strip()]
            
            print(f"[API] Running inference for symptoms: {symptoms}")
            
            # Run actual PLN inference engine!
            results = diagnose_patient(symptoms, top_k=5)
            
            # Format diagnostic results
            formatted_results = []
            for res in results:
                formatted_results.append({
                    "disease": res.disease,
                    "score": res.score,
                    "tv": {
                        "strength": res.tv.strength,
                        "confidence": res.tv.confidence
                    },
                    "coverage": res.coverage,
                    "matched_symptoms": res.matched_symptoms,
                    "total_symptoms": res.total_symptoms
                })
            
            # Get detailed reasoning explanation for top disease if available
            explanation = {}
            if results:
                top_disease = results[0].disease
                exp_data = explain_diagnosis(top_disease, symptoms)
                explanation = {
                    "disease": top_disease,
                    "matched_symptoms": exp_data["matched_symptoms"],
                    "unmatched_symptoms": exp_data["unmatched_symptoms"],
                    "rule_chain": exp_data["rule_chain"]
                }
            
            # Compile final response
            response_data = {
                "results": formatted_results,
                "explanation": explanation
            }
            
            # Send dynamic JSON response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_json = json.dumps(response_data)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            print(f"[API Error] {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            err_response = {"error": str(e)}
            self.wfile.write(json.dumps(err_response).encode('utf-8'))

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MedicalDemoRequestHandler)
    print(f"\n========================================================")
    print(f"OpenCog Medical PLN AI Web Server Running!")
    print(f"Local URL: http://localhost:{PORT}/demo.html")
    print(f"========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server. Goodbye!")
        sys.exit(0)

if __name__ == '__main__':
    run_server()
