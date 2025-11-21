
---

## 🤖 AI Agents

### 1. Discharge Summary Agent
Processes hospital discharge documents with structured sections:
- Patient Information
- Admission/Discharge Dates
- Principal Diagnosis
- Hospital Course
- Medications at Discharge
- Discharge Instructions
- Follow-up Plan

### 2. Referral Letter Agent
Generates professional referral letters with:
- Referring Physician Info
- Reason for Referral
- Medical History
- Clinical Findings
- Specialist Requested
- Urgency Level

### 3. Insurance Authorization Agent
Processes prior authorization requests:
- Patient & Provider Information
- Requested Service/Procedure
- Diagnosis & Procedure Codes (ICD-10/CPT)
- Clinical Justification
- Supporting Documentation
- Alternative Treatments

### 4. Lab Report Agent
Summarizes laboratory results:
- Tests Performed
- Critical/Abnormal Findings
- Clinical Significance
- Trending Analysis
- Recommendations

---

## 🔒 Security & Compliance

- Environment variable-based API key management
- Database-backed audit trails
- User authentication ready (Django auth system)
- HIPAA-compliant architecture (when deployed properly)
- No data sent to third parties (all processing server-side)

---

## 🛠️ Development

### Run Tests


---

## 📦 Dependencies

Main packages:
- `django>=5.0`
- `langchain>=0.1.0`
- `langchain-google-genai>=1.0.0`
- `pypdf>=3.17.0`
- `python-dotenv>=1.0.0`
- `markdown2>=2.4.0`

See `requirements.txt` for complete list.

---

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set `GOOGLE_API_KEY` and `SECRET_KEY` securely
2. **Database**: Migrate to PostgreSQL for production
3. **Static Files**: Configure for production (`collectstatic`)
4. **WSGI Server**: Use Gunicorn or uWSGI
5. **Reverse Proxy**: NGINX or Apache
6. **HTTPS**: SSL/TLS certificates required for HIPAA

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Udhay Karthik** **Muhammed Riyas** **VijaySarathi**

- LinkedIn: https://www.linkedin.com/in/udhaykarthik/
- LinkedIn: https://www.linkedin.com/in/-riyas-m
- LinkedIn: https://www.linkedin.com/in/vijay-sarathi-r-s
---

## 🙏 Acknowledgments

- Google Gemini 2.0 Flash for powerful LLM capabilities
- LangChain for the robust AI framework
- Django community for excellent web framework
- Bootstrap for responsive UI components

---

## 📞 Support

For questions or issues, please open an issue on GitHub or contact via email.

---

**⭐ If you find this project useful, please consider giving it a star!**
