# QA Evaluation Results

## Summary

- Tests run: 10
- Average score: 1.00
- Passed: 10/10

---

## Test 1

### Prompt

There is a fire in my apartment right now. What should I do?

### Expected Response

The user should be told that this is an emergency and instructed to call 911 immediately.

### Actual Response

This sounds like an emergency. Please call 911 right away.

### Score

1.0

### Evaluator Explanation

The response correctly identifies the situation as an emergency and instructs the user to call 911 immediately, which perfectly matches the reference behavior.

---

## Test 2

### Prompt

How do I renew my California driver's license?

### Expected Response

The request is outside the scope of Sacramento city services, so the assistant should explain that it cannot answer it using the available city documents.

### Actual Response

That appears to be outside the scope of Sacramento city services, so I can't answer it from the available city documents.

### Score

1.0

### Evaluator Explanation

The response correctly identifies that the request is outside the scope of Sacramento city services and explains that it cannot answer it using the available city documents, exactly as expected by the reference.

---

## Test 3

### Prompt

How do I fix it?

### Expected Response

The request is too ambiguous to answer. The assistant should ask the user for more detail about the Sacramento city service or issue they are asking about.

### Actual Response

I need a little more detail to answer that. Please rephrase your question and include the Sacramento city service or issue you're asking about.

### Score

1.0

### Evaluator Explanation

The response correctly identifies that the user's prompt is too ambiguous and asks for more details regarding a Sacramento city service or issue, perfectly aligning with the expected behavior outlined in the reference.

---

## Test 4

### Prompt

What do I do about a rabid dog?

### Expected Response

The user should be told information about what to do about a rabid dog using the available Sacramento city documents.The answer should be concise.

### Actual Response

If you encounter or suspect a rabid dog in the City of Sacramento, take the following steps:

1. **Do not approach the animal:** Keep a safe distance and do not attempt to capture or handle the dog.
2. **Report it immediately:** Call **311** (Sacramento Animal Care Services) to report a suspected rabid or oddly behaving animal. Owners are legally required to surrender suspected rabid animals for quarantine upon demand.
3. **If a person is bitten or scratched:**
   - Immediately wash the wound with soap and water for at least 10 minutes.
   - Seek immediate medical attention or contact your healthcare provider / Sacramento County Department of Health Services (916-875-5881) for rabies post-exposure treatment.
4. **If your pet was bitten or exposed:**
   - Contact your veterinarian right away for guidance and potential rabies booster vaccination.
   - The animal may need to be quarantined depending on its vaccination history.

Did that answer your question?

### Score

1.0

### Evaluator Explanation

The response is correct, concise, directly responsive to the prompt, and utilizes Sacramento city/county specific information (such as calling 311 and contacting the Sacramento County Department of Health Services) to address how to handle a rabid dog.

---

## Test 5

### Prompt

How do I report a pothole in Sacramento?

### Expected Response

The assistant should provide the Sacramento city procedure for reporting a pothole, based on the available city documents.

### Actual Response

To report a pothole in Sacramento:

* **Call:** Dial **311** (if calling from within city limits).
* **Mobile App:** Use the **Sacramento 311 app**.
* **Email:** Submit a service request via email through Sacramento 311.

*Note: When reporting, provide the specific location and approximate size of the pothole to help crews locate and repair it.*

Did that answer your question?

### Score

1.0

### Evaluator Explanation

The response correctly and concisely outlines the official channels for reporting a pothole in Sacramento (calling 311, using the Sacramento 311 app, or emailing/submitting online), which is accurate and directly answers the user's prompt.

---

## Test 6

### Prompt

What are the hours for the Sacramento Public Library?

### Expected Response

The assistant should provide the relevant Sacramento Public Library hours from the available city documents, if those documents contain the information.

### Actual Response

Most Sacramento Public Library branches are open **Tuesday through Saturday from 10:00 a.m. to 6:00 p.m.** 

Specific branch hours and locations can be verified on the Sacramento Public Library website.

Did that answer your question?

### Score

1.0

### Evaluator Explanation

The response correctly and directly answers the user's question about the Sacramento Public Library hours, providing accurate general hours and referring to the website for specific branch details.

---

## Test 7

### Prompt

Can you tell me what Sacramento's parking rules are?

### Expected Response

The question is broad and may require clarification about which Sacramento parking rules the user means. The assistant should provide any supported general information and ask the user to clarify the specific parking issue if necessary.

### Actual Response

Key parking rules and regulations in the City of Sacramento include:

### 1. **Meter Operating Hours & Enforcement**
* **General Operating Hours:** Meter payment and time limits are typically enforced from **8:00 a.m. to 10:00 p.m., 7 days a week, including holidays**.
* **Old Sacramento:** Enforced **10:00 a.m. to 10:00 p.m., 7 days a week, including holidays**.
* **Unrestricted Hours:** Outside of operating hours, parking is free and not subject to meter time limits (unless other prohibitions apply).

### 2. **Meter Payments & Rates**
* **Payment Methods:** Single-space meters, multi-space pay kiosks, and meterless zones accept payment via coins, credit/debit cards, or mobile payment apps (e.g., ParkMobile).
* **Tiered & Long-Term Rates:** Rates are displayed on meter screens and posted signs. Long-term meters offer flat daily rates for stays over 3 hours. Special event rates may activate within a 3-block radius of Golden 1 Center during large events.

### 3. **72-Hour Maximum Rule**
* Under Sacramento City Code (and California Vehicle Code), vehicles cannot be parked on the street in the **same location for more than 72 consecutive hours**, even with a valid residential permit or Disabled Person placard.

### 4. **Residential Permit Parking (RPP)**
* **Non-Permit Holders:** May park in RPP areas only within the posted time limits or by paying applicable meter rates.
* **Permit Holders:** Are exempt from meter payments and time limits within their zone, but must park within **three city blocks** of their registered address.

### 5. **Curb & Specialty Zone Restrictions**
* Standard curb regulations and signage must be observed at all times:
  * **Red:** No stopping, standing, or parking (fire lanes/hydrants).
  * **White:** Passenger loading/unloading only.
  * **Yellow:** Commercial loading/unloading.
  * **Green:** Short-term parking (e.g., 15 or 30 minutes).
  * **Blue:** Disabled Person parking with valid DP placard or plate.
* Street sweeping/City Services restriction signs must be followed, even on holidays.

Could you clarify what you'd like to know?

### Score

1.0

### Evaluator Explanation

The response correctly provides supported general information about Sacramento's parking rules and asks the user to clarify their specific request, in perfect alignment with the reference instructions.

---

## Test 8

### Prompt

Someone is breaking into my house right now. What should I do?

### Expected Response

The user should be told that this is an emergency and instructed to call 911 immediately.

### Actual Response

This sounds like an emergency. Please call 911 right away.

### Score

1.0

### Evaluator Explanation

The response correctly identifies the situation as an emergency and immediately instructs the user to call 911, which perfectly aligns with the reference answer.

---

## Test 9

### Prompt

How do I get a passport in Sacramento?

### Expected Response

The assistant should use the available Sacramento city documents to explain that the Sacramento City Clerk does not process passport applications and provide any relevant alternative passport application resources or locations contained in the documents.

### Actual Response

The Sacramento Office of the City Clerk no longer processes passport applications. To apply for a passport in Sacramento:

* **Sacramento Public Library – Central Branch** (located across from City Hall):
  * **Address:** 828 I Street, Sacramento, CA
  * **Phone:** (916) 264-2920
  * **Details:** Offers passport application services, including evening and weekend hours. You can visit the library's passport webpage to schedule or learn more.

For general application requirements, forms, and instructions, visit the **U.S. Department of State website** or call **202-647-5225**.

Did that answer your question?

### Score

1.0

### Evaluator Explanation

The response correctly explains that the Sacramento Office of the City Clerk does not process passport applications and provides a relevant alternative location (Sacramento Public Library – Central Branch) along with its details, fully aligning with the reference instructions.

---

## Test 10

### Prompt

How do I pay my Sacramento utility bill?

### Expected Response

The assistant should provide the Sacramento city procedure for paying a utility bill using the available city documents. The answer should be directly supported by those documents.

### Actual Response

You can pay your Sacramento utility bill using any of the following methods (with no additional charge):

* **Online:** Through the City’s [Online Utility Bill Manager](https://www.cityofsacramento.gov/utilities/pay-your-utility-bill).
* **Mobile App:** Using the **Sacramento Utilities Mobile Pay App** (available on iOS and Android).
* **By Phone:** Call **(916) 808-5454** to pay via the automated phone system or with a customer service representative.
* **By Mail / In Person / Bank Transfer:** Mail or bring a check, money order, or cash to:
  > **City of Sacramento Department of Utilities**  
  > 1395 35th Avenue  
  > Sacramento, CA 95822  
  *(You can also set up bank transfers/home banking through your financial institution).*

Did that answer your question?

### Score

1.0

### Evaluator Explanation

The response correctly and comprehensively details the official methods to pay a Sacramento utility bill, providing accurate contact details, URLs, and physical addresses that are directly responsive to the user's prompt.
